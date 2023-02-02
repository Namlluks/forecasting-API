from pydantic import BaseModel, Field
from typing import Union

# 

class CountryMethaneInfos(BaseModel):
    iso2code: str = Field(description="the country code in 2 characters")
    country_name: str = Field(description="the country name")
    population: Union[int, None] = Field(default = None, description="the population of the country")
    methane_emissions: Union[float, None] = Field(default = None, description="the methane emission (kt of CO2 equivalent)")
    is_predicted: Union[bool, None] = Field(default = None, description="if the result comes form a predictio")
    uncertainty: Union[dict, None] = Field(default = None, description="the upper and lower range of uncertainty")
    score: Union[float, None] = Field(default = None, description="a score from 0 to 10 about the impact of the country")
    methane_emissions_by_population: Union[float, None] = Field(default = None, description="the emission by the population")
