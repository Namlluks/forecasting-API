class Linking:
	import requests, json, os
	import pandas as pd
	from tqdm import tqdm

	def __init__(self, save_data = True, load_data = True):
		self.base_url = "http://api.worldbank.org/v2/country/all{}?format={}&per_page=500&page={}"
		self.datas = {}

		self.save_data = save_data
		self.load_data = load_data

	# Format the url
	def _url_formater(self, target, output_format, page):
		return self.base_url.format(target, output_format, page)

	# Clean and transform datas
	def _clean(self, target):
		if target in ["/indicator/EN.ATM.METH.KT.CE", "/indicator/SP.POP.TOTL"]:
			self.datas[target] = self.datas[target][["country", "countryiso3code", "date", "value"]]
			self.datas[target]["country"] = self.datas[target]["country"].apply(lambda x: x["value"])
			self.datas[target] = self.datas[target].sort_values("date")
			self.datas[target]["date"] = self.pd.to_datetime(self.datas[target]["date"], format ="%Y")
			self.datas[target]["date"].asfreq('d')
			
		if target in ["/"]:
			self.datas[target]["incomeLevel"] = self.datas[target]["incomeLevel"].apply(lambda x: x["value"])

	# Handle pages calls
	def _data_handler(self, url, target):
		if target not in self.datas:
			self.datas[target] = self.pd.DataFrame()

		try:
			r = self.requests.get(url)
			r.raise_for_status()
		except (self.requests.exceptions.ConnectionError, self.requests.exceptions.Timeout):
			raise Exception( {"status": 503, "url": url} )
		except self.requests.exceptions.HTTPError:
			raise Exception( {"status": r.status_code, "url": url} )
		else:
			self.datas[target] = self.pd.concat([self.datas[target], self.pd.DataFrame(r.json()[1])])
			return r.json()

	# Cache data (speedup serveur start, no need to load data every times in our case)
	def _save_data(self, target):
		path = "./cache/{}.csv".format(target.replace("/", "_"))
		self.datas[target].to_csv(path, index=False)

	# If we save, them ...
	def _load_data(self, target):
		path = "./cache/{}.csv".format(target.replace("/", "_"))
		if self.os.path.isfile(path):
			self.datas[target] = self.pd.read_csv(path)
			return True
		return False

	# Get data form an url
	def _get_datas(self, target):
		if self.load_data:
			if self._load_data(target):
				return

		url = self._url_formater(target, "json", 1)
		req = self._data_handler(url, target)

		for i in self.tqdm(range(req[0]["pages"] - 1), desc=f'Getting datas for \"{target}\"'):
			url = self._url_formater(target, "json", i + 2)
			self._data_handler(url, target)

		if len(self.datas[target]) != req[0]["total"]:
			raise Exception("Something went wrong : {} != {}".format(self.datas[target]), req[0]["total"])
		self.datas[target].reset_index(drop=False, inplace=True)

		self._clean(target)

		if self.save_data:
			self._save_data(target)

	# Get data form an url
	def get_datas(self, targets):
		if type(targets) == str:
			self._get_datas(targets)
		if type(targets) == list:
			for target in targets:
				self._get_datas(target)

		return self

	# Load a part of datas
	def load(self, target = None):
		if target == None:
			return self.datas
		return self.datas[target]