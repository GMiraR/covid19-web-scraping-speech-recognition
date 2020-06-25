#don't forget to install the 'requests' package on pip
'''
IMPORTANT

INSTALL THESE: 

pywin32
SpeechRecognition
pyttsx3

pyaudio ---> go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
and look for the version that corresponds to your python version 
'''
import requests
import json
#try 'python -m pip install pyttsx3==2.71' if problems with pyttsx3
import speech_recognition as sr
import pyttsx3

import re #ReGex

import time
import threading


#setup keys for the project
API_KEY = 'twKpMoUH58W5'
PROJECT_TOKEN = 'tEokKmJTjNL3'
RUN_TOKEN = 'tPO6FhOE159B'


class Data:
	# the constructor for the Data object
	def __init__(self, api_key, project_token):
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			'api_key': self.api_key
		}
		self.data = self.get_data()

	#getting the data from the API		
	def get_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
		#loading the data from the api
		data = json.loads(response.text)
		return data

	def get_total_cases(self):
		data = self.data['total']

		#loop to encounter the value of total cases inside coronavirus cases
		for content in data:
			if content['name'] == 'Coronavirus Cases:':
				return content['value']

	def get_total_deaths(self):
		data = self.data['total']

		#loop to encounter the value of total deaths inside coronavirus cases
		for info in data:
			if info['name'] == 'Deaths:':
				return info['value']

	def get_country_info(self, country):
		data = self.data['country']

		for info in data:
			#comparing the info at the position of 'name' with the country parameter
			if info['name'].lower() == country.lower():
				return info
		return '0'

	def update_dataset(self):
		response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
		

		def changes():
			time.sleep(0.1)
			#old data
			o_data = self.data
			while True:
				n_data = self.get_data()
				if n_data != o_data:
					self.data = n_data
					print('data updated.')
					break
				time.sleep(5)

		thread = threading.Thread(target=changes)
		thread.start()

	def get_countries(self):
		data = self.data['country']
		
		list_of_countries = [country['name'].lower() for country in data]

		return set(list_of_countries)

	def get_country_deaths(self, country):
		return data.get_country_info(country)['total_deaths']

	def get_country_recovereds(self, country):
		return data.get_country_info(country)['total_recovered']



#to look all the data
#print(data.data)

##########################################
##########################################
#testing the methods from the class Data

# print(data.get_total_cases())
# print(data.get_total_deaths())

# print(data.get_country_info('USA'))
# print(data.get_country_info('USA')['total_tests'])
# print(data.get_country_deaths('brazil'))
# print(data.get_country_recovereds('brazil'))

# print(data.get_countries())


def speak(text):
	engine = pyttsx3.init()

	en_voice_id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"

	engine.setProperty('voice', en_voice_id)

	engine.say(text)
	engine.runAndWait()

def get_audio():
	recog = sr.Recognizer()
	with sr.Microphone() as source:
		audio = recog.listen(source)
		said = ''

		try:
			said = recog.recognize_google(audio)
		except Exception as e:
			print('Exception', str(e))
	
	return said.lower()



def main():
	print('Started.')
	#if the program heards 'stop' it'll stop
	END = 'stop'
	

	#instantiation of data, giving api and project_token
	data = Data(API_KEY, PROJECT_TOKEN)

	country_list = data.get_countries()

	REGEX_FOR_TOTAL = {
					  # Any pattern of words + the word 'total' + any pattern of words + 'cases'
					  # Then call the get_total_cases() function
					  re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
					  re.compile("[\w\s]+ total cases"):data.get_total_cases,

					  re.compile("[\w\s]+ total [\w\s]+ deaths"):data.get_total_deaths,
					  re.compile("[\w\s]+ total deaths"):data.get_total_deaths

					 }

	REGEX_FOR_COUNTRIES = {
					   	re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_info(country)['total_cases'],
                    	re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_info(country)['total_deaths'],
                    	# FIX LATER #re.compile("[\w\s]+ [recovereds|recovered] [\w\s]+"): lambda country: data.get_country_info(country)['total_recovered']
					   }

	UPDATE = "update"

	while True:
		print('Listening...')
		text = get_audio()
		print(text)
		result = None


		for pattern, func in REGEX_FOR_COUNTRIES.items():
			if pattern.match(text):
				words = set(text.split(" "))
				for country in country_list:
					if country in words:
						result = func(country)
						break

		#looping through the dict of patterns
		for pattern, func in REGEX_FOR_TOTAL.items():
			#match is a regex method, if matches with text "audio we gave to the program"
			#call the function associeted with the pattern
			if pattern.match(text):
				result = func()
				break

		if text == UPDATE:
			result = "Data is being updated!"
			data.update_dataset()


		if result:
			speak(result)

		#to break the loop
		if text.find(END) != -1:
			print('The program stopped!')
			break

main()