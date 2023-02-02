from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_main():
    response = client.get("/")
    assert response.status_code == 200

def test_forecasting_country_emissions():
    response = client.get("/forecasting/get_country_emissions")
    assert response.status_code == 422
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "FRA"})
    assert response.status_code == 200
    assert response.json() == {
		"iso2code": "FR",
		"country_name": "France",
		"population": None,
		"methane_emissions": None,
		"is_predicted": None,
		"uncertainty": None,
		"score": None,
		"methane_emissions_by_population": None
	}
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "XXX"})
    assert response.status_code == 404
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": 12})
    assert response.status_code == 422
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "FRA", "year": "test"})
    assert response.status_code == 422
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "FRA", "year": 2035})
    assert response.status_code == 422
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "FRA", "year": 2000})
    assert response.status_code == 422
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "FRA", "year": 2020})
    assert response.status_code == 200
    assert response.json() == {
		"iso2code": "FR",
		"country_name": "France",
		"population": 67571107,
		"methane_emissions": 59635.80484069391,
		"is_predicted": True,
		"uncertainty": {
			"lower value": 57885.512078709886,
			"upper value": 61386.09760267794
		},
		"score": 1.702,
		"methane_emissions_by_population": 0.0008825636797794938
	}
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "FRA", "year": 2028})
    assert response.status_code == 200
    assert response.json() == {
		"iso2code": "FR",
		"country_name": "France",
		"population": None,
		"methane_emissions": 59555.159512042745,
		"is_predicted": True,
		"uncertainty": {
			"lower value": 54217.149478167696,
			"upper value": 64893.16954591779
		},
		"score": None,
		"methane_emissions_by_population": None
	}
    response = client.get("/forecasting/get_country_emissions", params={"iso_code": "FRA", "year": 2013})
    assert response.status_code == 200
    assert response.json() == {
	  "iso2code": "FR",
	  "country_name": "France",
	  "population": 66002289,
	  "methane_emissions": 64849.9984741211,
	  "is_predicted": False,
	  "uncertainty": None,
	  "score": 1.895,
	  "methane_emissions_by_population": 0.0009825416581252372
	}