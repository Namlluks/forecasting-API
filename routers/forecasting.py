from fastapi import APIRouter, Query, HTTPException
from typing import Union

import datetime, pandas, numpy

from utils.linking import Linking
from utils.forecasting import Forecasting

from models.forecasting import CountryMethaneInfos

router = APIRouter()

# Loading datas
linker = Linking(save_data = True, load_data = True)
linker.get_datas(["/indicator/SP.POP.TOTL", "/indicator/EN.ATM.METH.KT.CE", "/"])
loaded_datas = linker.load()
linker = Linking(save_data = True, load_data = True)

# Simplify the use of datas
loaded_datas["methane"] = loaded_datas["/indicator/EN.ATM.METH.KT.CE"].dropna()
del loaded_datas["/indicator/EN.ATM.METH.KT.CE"]
loaded_datas["population"] = loaded_datas["/indicator/SP.POP.TOTL"]
del loaded_datas["/indicator/SP.POP.TOTL"]
loaded_datas["infos"] = loaded_datas["/"]
del loaded_datas["/"]

loaded_datas["merged"] = pandas.merge(loaded_datas["methane"].rename(columns={"value": "methane_emissions"}), loaded_datas["population"].drop("country", axis = 1).rename(columns={"value": "population"}), on=["countryiso3code", "date"])
loaded_datas["merged"]["methane_emissions_per_population"] = loaded_datas["merged"]["methane_emissions"] / loaded_datas["merged"]["population"]

# Forecasting engine
forcasting = Forecasting()
loaded_datas["methane"]["date"].asfreq('y')
loaded_datas["methane"].index = loaded_datas["methane"]["date"]
frc = Forecasting().load_datas(loaded_datas["methane"])





iso_code_q = Query(detail = "The ISO country code, in 3 characters", min_length=3, max_length=3) # regex exist, but will be redundant here
years_q = Query(default=None, ge=2013, le=2028)
@router.get("/get_country_emissions", summary="Get country emissions and predict it if not evailable", response_model=CountryMethaneInfos)
async def get_country_emissions(iso_code: str = iso_code_q, year: int = years_q):
	"""
		For a country (as iso3code) and a year (optional).
		Return : 

		- "methane_emissions": the methane emission (kt of CO2 equivalent)
		- "is_predicted": if the result comes form a prediction
		- "iso2code": the country code in 2 characters
		- "country_name": the country name
		- "uncertainty": the upper and lower range of uncertainty
		- "score": a score from 0 to 10 about the impact of the country
		- "population": the population of the country
		- "methane_emissions_by_population": the emission by the population
	"""
	if iso_code not in loaded_datas["methane"]["countryiso3code"].unique():
		raise HTTPException(status_code=404, detail="Country code not found")

	if year != None:
		year = f"{year}-01-01"

	res = {
		"iso2code": loaded_datas["infos"][loaded_datas["infos"]["id"] == iso_code]["iso2Code"].iloc[0],
		"country_name": loaded_datas["methane"][loaded_datas["methane"]["countryiso3code"] == iso_code]["country"].iloc[0]
	}


	mask1 = (loaded_datas["methane"]["date"] == year) # date
	mask2 = (loaded_datas["methane"]["countryiso3code"] == iso_code) # contry code
	current_methane = loaded_datas["methane"][mask1 & mask2]

	if len(current_methane) != 0:
		current_methane = current_methane.iloc[0]["value"]
		is_predicted = False
		res["is_predicted"] = is_predicted
		res["methane_emissions"] = current_methane
	else:
		if year != None:
			y, preds, confident = frc.predict("ARIMA", iso_code, year, year)
			current_methane = preds[year]
			is_predicted = True
			uncertainty = confident.T[year].to_dict()
			res["uncertainty"] = uncertainty
			res["is_predicted"] = is_predicted
			res["methane_emissions"] = current_methane

	mask1 = (loaded_datas["population"]["date"] == year) # date
	mask2 = (loaded_datas["population"]["countryiso3code"] == iso_code) # contry code

	population = loaded_datas["population"][mask1 & mask2]["value"]
	if len(population) != 0:
		res["population"] = population.iloc[0]
		
	# Scoring simple
	if "methane_emissions" in res and "population" in res:
		score = (current_methane / res["population"])
		score /= loaded_datas["merged"]["methane_emissions_per_population"].median()
		score = 10 if score*2 > 10 else round(score*2, 3)
		res["score"] = score
		res["methane_emissions_by_population"] = current_methane/res["population"]

	return res
