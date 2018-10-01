# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext, loader
import requests, json
from django.core.cache import cache,caches  
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta	
# Create your views here.

def home(request):
	if request.user == 'MODERATOR':
		return HttpResponseRedirect('signup')
	if request.user == 'ADMIN':
		return HttpResponseRedirect('route')
	if request.user == 'PLAYER':
		return HttpResponseRedirect('task')
	if request.user is None:
		return HttpResponseRedirect('login')

def test(request):
	return HttpResponse(request.user)

def logout_view(request):
	key=request.COOKIES.get('sessid')
	response = HttpResponseRedirect('login')
	response.delete_cookie('sessid')
	response.delete_cookie('team_type')
	response.delete_cookie('team_id')
	cache.delete('sessid')
	cache.delete('team_type')
	cache.delete('teamID')
	return response

def login_view(request):
	error = ''
	if request.method == 'POST':
		login = request.POST.get('login')
		password = request.POST.get('password')
		url = request.POST.get('continue', '/')
		sessid = do_login(login,password)
		if sessid['sessid'] is not None:
			response = HttpResponseRedirect(url)
			response.set_cookie('sessid', sessid['sessid'])
			response.set_cookie('team_type', sessid['teamType'])
			response.set_cookie('team_id', sessid['teamID'])
			print('send-response')
			return response
		else: 
			error = u'Неверный логин / пароль'
	return render(request, 'App/auth/login.html', {'error': error})

def do_login(login, password):
	from django.core.cache import cache
	url = 'http://138.68.173.73:8080/auth'
	headers = {
  		'Content-Type': 'application/json'
	}
	json_text = {
		'login': login,
	 	'password': password
	 }
	r = requests.post(url, json=json_text, headers=headers)
	if (r.status_code == 200):
		sessid = get_random_string(length=32)
		cache.set('sessid', sessid,3600*3)
		json_response = r.json()
		teamType = json_response['teamType']
		teamID = json_response['teamID']
		print(json_response['teamID'])
	else:
		sessid = None
		teamType = None
	return {'sessid': sessid, 'teamType': teamType, 'teamID': teamID}

def addMembertoJson(request, registration_data):
	first_name = 'memberFirstName'
	second_name = 'memberSecondName'
	firstextramember = 4
	lastextramember = 7
	for i in range(firstextramember,lastextramember):
		member = {
		'first_name': request.POST.get(first_name+str(i)),
		'second_name': request.POST.get(second_name+str(i))
		}					
		add_member(member,registration_data)

def signup(request):
	if request.user == 'MODERATOR':
		if request.method == 'POST':
			url = 'http://138.68.173.73:8080/moderator/team'
			headers = {'Content-Type': 'application/json'}
			registration_data = {
	    		"team_name": request.POST.get('team_name'),
	    		"leader": {
	      		"first_name": request.POST.get('teamleadFirstName'),
	      		"second_name": request.POST.get('teamleadSecondName')
	    	},
	    	"members": [
		      	{
		        	"first_name": request.POST.get('memberFirstName1'),
		        	"second_name": request.POST.get('memberSecondName1')
		      	},
		      	{
					"first_name": request.POST.get('memberFirstName2'),
					"second_name": request.POST.get('memberSecondName2')
				},	  
				{
					"first_name": request.POST.get('memberFirstName3'),
					"second_name": request.POST.get('memberSecondName3')
				}	  		
		    ]
	  		}
	  		
	#Добавление новых участников команды для отправки на игровой сервер
			addMembertoJson(request,registration_data)
	  		r = requests.post(url, json=registration_data, headers=headers)
	  		return HttpResponseRedirect('signup')
	  	else:
	  		return render(request, 'App/admin/signup.html')
	else: 
		return HttpResponse("Эта страница доступна только модераторам")


def add_member(member,registration_data):
		if member['first_name'] is not None:
 				registration_data["members"].append(member)
 		else:
 			return

def proxy_request(request):
	full = request.GET.get('isCheckbox')
	url='http://138.68.173.73:8080/moderator/team?full='+full
	headers = {'Content-Type': 'application/json'}
	r=requests.get(url,headers=headers)
	return r.json()

def score_table(request):
	if request.is_ajax():
		data=proxy_request(request)
		return JsonResponse(data)
	if request.method == 'GET':
		if request.user == 'MODERATOR':
			return render(request,'App/admin/score_table_moderator.html')
		if request.user == 'ADMIN':
			return render(request,'App/admin/score_table_admin.html')
	


def get_current_task(request):
	print('get current task')
	teamID = request.COOKIES.get('team_id')
	print(teamID)
	url = 'http://138.68.173.73:8080/player/task/' + str(teamID)
	headers = {'Content-Type': 'application/json'}
	r = requests.get(url,headers)
	print(r.json())
	return r

def get_next_task(request):
	print('get next task')
	task_id = cache.get('task_id')
	team_id = request.COOKIES.get('team_id')
	task_type = cache.get('task_type')
	print(task_type)
	print(team_id)
	url = 'http://138.68.173.73:8080/player/next'
	headers = {'Content-Type': 'application/json'}
	data =  {
	   "team_id": team_id,
	   "task_id": task_id,
	   "task_type": task_type
	  }
	print(data)
	r = requests.post(url, json=data, headers=headers)
	print(r.json())
	return r

def render_task_photo_or_extra(request, resp):
	task_id = resp['task_id']	
	task_type = resp['task_type']
	points = resp['points']
	template = 'App/player/' + task_type + '/' +'task.html'
	cache.set_many({'points': points,
					'task_id': task_id,
					'task_type': task_type})
	return render(request, template, resp)

def check_task(request, r):
	resp = r.json()
	print('check task')
	print(r.status_code)
	print(resp)
	if r.status_code == 200:
		if resp['is_finished']:
			return HttpResponse("Вы прошли все задания текущего этапа")
		if resp['is_answered']:
			points = cache.get('points')
			duration = cache.get('duration')
			started = cache.get('started')
			print("is_answered")
			return render(request, 'App/player/FINAL/next_task.html', {'points': points, 'duration': duration, 'started': started})
		if resp['task_type'] == 'PHOTO' or resp['task_type'] == 'EXTRA':
			return render_task_photo_or_extra(request, resp)
		else:
			task_id = resp['task_id']	
			task_type = resp['task_type']
			points = resp['points']	
			started = resp['start_time']
			duration = resp['duration']
			template = 'App/player/' + task_type + '/' +'task.html'
			cache.set_many({'points': points,'task_id': task_id,'task_type': task_type,'duration': duration,'started': started})
			data=cache.get_many(['points','task_id','task_type','duration','started'])
			print('print cache')
			print(data)
			return render(request, template, data)
	if r.status_code == 204:
		weekday = datetime.today().weekday()
		if (weekday > 0) and (weekday != 5):
			msg = 'Ждём вас в понедельник'	
		if weekday == 5:
			msg = 'Первый этап закончен. Подходите 12.10 в выбранное время на портал в гз'
		#return render(request, 'App/player/no-info.html', msg)
		return HttpResponse(msg)
	if r.status_code >= 400:
		# ошибка 403: сначала ответьте на текущее задание. Нужно перевести игрока на current_task
		# с помощью подсказок либо автоматом
		# на остальные сообщения нужно сделать шаблон с выходом в главное меню и выводом сообщения 
		# об ошибке и дальнейшими инструкциями 
		return HttpResponse(resp['message'])

def check_answer(request, r, answer):
	resp = r.json()
	print(resp)
	if r.status_code == 202:
		if resp['task_type'] == 'FINAL':		
			if resp['is_correct']:
				return JsonResponse({'status': 'True', 'task_type': resp['task_type']})
			else:
				return JsonResponse({'status': 'False', 'task_type': resp['task_type']})
		if resp['task_type'] == 'EXTRA':
			if resp['is_correct']:
				return JsonResponse({'status': 'True', 'task_type': resp['task_type'], 'tooltip': resp['tooltip']})
			else:
				return JsonResponse({'status': 'False', 'task_type': resp['task_type']})
		else:
			if resp['is_correct']:
				return JsonResponse({'status': 'True', 'task_type': resp['task_type']})
			else:
				return JsonResponse({'status': 'False', 'task_type': resp['task_type']})
	if r.status_code >= 400:
		# написать нормальные обработчики ошибок с вставкой сообщений в шаблон
		# и инструкциями по дальнейшим действиям
		msg = r.json()
		msg = msg['message']
		return HttpResponse(msg)

def send_answer(request):
	task_id = cache.get('task_id')
	team_id = request.COOKIES.get('team_id')
	task_type = cache.get('task_type')
	answer = request.POST.get('answer')
	url = 'http://138.68.173.73:8080/player/task'
	headers = {'Content-Type': 'application/json'}
	data =  {
	   "team_id": team_id,
	   "task_id": task_id,
	   "answer": answer,
	   "task_type": task_type
	  }
	cache.set('answer', answer)
	print('sended answer data: ')
	print(data)
	r = requests.post(url, json=data, headers=headers)
	print(r.status_code)
	return check_answer(request, r, answer)

def task_view(request):
	if request.is_ajax(): # answer comes from ajax-request
		if request.method == 'POST': 
			print('sended answer')
			return send_answer(request)	
	if request.method == 'GET':
		if request.GET.get('next'):		
			answer = cache.get('answer')
			points = cache.get('points')
			duration = cache.get('duration')
			started = cache.get('started')
			return render(request, 'App/player/FINAL/next_task.html', {'answer': answer, 'points': points, 'duration': duration, 'started': started })
		if (request.GET.get('submit') == 'Перейти к следующему этапу'):
			r = get_next_task(request)
			return check_task(request, r)
		r = get_current_task(request)
		return check_task(request, r)
	

def team_info(request):
	teamID = request.COOKIES.get('team_id')
	url = 'http://138.68.173.73:8080/player/team/' + str(teamID)
	headers = {'Content-Type': 'application/json'}
	r = requests.get(url,headers)
	resp = r.json()
	print(resp)
	try: 
		time = resp['start_time']
		time = datetime.utcfromtimestamp(float(time)).strftime('%Y.%m.%d %H:%M:%S')
		resp.update({'start_time': time})
		return render(request, 'App/player/team_page.html', resp)
	except KeyError: 
		resp.update({'start_time': 'Уточняется'})
		return render(request, 'App/player/team_page.html', resp)
	

def team_info_moderator(request):
	teamID = cache.get('team_id')
	url = 'http://138.68.173.73:8080/moderator/team/' + str(teamID)
	headers = {'Content-Type': 'application/json'}
	r = requests.get(url,headers)
	resp = r.json()
	try: 
		time = resp['start_time']
		time = datetime.utcfromtimestamp(float(time)).strftime('%Y.%m.%d %H:%M:%S')
		resp.update({'start_time': time})
		return render(request, 'App/player/moderator_team_page.html', resp)
	except KeyError: 
		return HttpResponseRedirect('/') 

def team_search(request):
	if request.user != 'MODERATOR':
		return render(request, 'App/main/error.html', {'error_msg': 'Необходимо обладать правами модератора, чтобы просматривать эту страницу'})
	teamID = request.GET.get('teamID')
	print(teamID)
	if teamID != None:
		url = 'http://138.68.173.73:8080/moderator/prepare/' + str(teamID)
		headers = {'Content-Type': 'application/json'}
		r = requests.get(url,headers)
		print(r.status_code)
		if r.status_code == 200:
			resp = r.json()
			print(resp)
			try: 
				time = resp['start_time']
				time = datetime.utcfromtimestamp(float(time)).strftime('%Y.%m.%d %M:%S')
				resp.update({'start_time': str(time)})
			except KeyError: 
				HttpResponseRedirect('/') 
			except TypeError:
				resp.update({'start_time': 'Уточняется'})
			return render(request, 'App/admin/start-finish.html', resp)
		if r.status_code >=400:
			return render(request, 'App/admin/start-finish.html', {'error_msg': 'Данных о запрашиваемой команде не существует'})
	else: 
		return render(request, 'App/admin/start-finish.html')

def start(request):
	if request.method == 'POST':
		teamID = request.POST.get('teamID')
		print(teamID)
		url = 'http://138.68.173.73:8080/moderator/start/' + str(teamID)
		print(url)
		headers = {'Content-Type': 'application/json'}
		r = requests.get(url,headers)
		print(r.status_code)
		if r.status_code == 202:
			return render(request, 'App/admin/start-finish.html', {'success':'Команда стартовала'})
		else:
			return render(request, 'App/admin/start-finish.html', r.json())

def finish(request):
	if request.method == 'POST':
		teamID = request.POST.get('teamID')
		url = 'http://138.68.173.73:8080/moderator/stop/' + str(teamID)
		headers = {'Content-Type': 'application/json'}
		r = requests.get(url,headers)
		if r.status_code == 202:
			return render(request, 'App/admin/start-finish.html',{'succes':'Команда успешно финишировала'})
		else:
			return render(request, 'App/admin/start-finish.html',r.json())


def team_search_key(request):
	if request.user != 'MODERATOR':
		return render('App/main/error.html', {'error_msg': 'Необходимо обладать правами модератора, чтобы просматривать эту страницу'})
	#teamID = request.GET.get('teamID')
	teamID = request.GET.get('teamID')
	if teamID is None:
		return render(request, 'App/admin/moderator-search.html')
	url = 'http://138.68.173.73:8080/moderator/photo/' + teamID
	headers = {'Content-Type': 'application/json'}
	print(url)
	r = requests.get(url,headers)
	print(r)
	return render(request, 'App/admin/moderator-search.html', r.json())

def route(request):
	if request.user != 'ADMIN':
		return render(request, 'App/main/error.html', {'error_msg': 'Необходимо обладать правами администратора, чтобы просматривать эту страницу'})
	if request.is_ajax():
		full = request.GET.get('isCheckbox2')
		url = 'http://138.68.173.73:8080/admin/router?full=' + full	
		headers = {'Content-Type': 'application/json'}
		r = requests.get(url,headers)
		print(r.json())
		return JsonResponse(r.json())
	return render(request,'App/admin/route.html')


