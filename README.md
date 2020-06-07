# [Misschedule](http://ec2-18-196-114-33.eu-central-1.compute.amazonaws.com/ 'Перейти на сайт')
## Техническое задание
Создать приложение и api планировщика дел и проектов с целью экономия времени людей на Flask 

## Библиотеки
 В проекте были использованы такие библиотеки как Flask, Flask-wtf, Flask-login, sqlalchemy, werkzeug и другие
 библиотеки, которые можно найти, заглянув в requirements.txt
 
## Работа проекта
* ### Api
Api реализовано как Flask-приложение (папка api) в виде микросервисов, которое нужно для получения и обработки
даннх о проектах, пользователях и чатах. Оно запускается на порте 5000. 
* ### Сайт
Сайт - это ещё одно Flask-приложение (папка misschedule), которое осуществляет взаимдействие пользователя с Api
через интренет. Оно запускается на порте 8080.
* ### Необходимость Api
Api необходим для возможности реализации приложения на нескольких платформах. Можно создать не
только сайт, но и мобильное или desktop приложения на базе текущего Api.

Api протестирован с помощью Postman  
[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/864c009340669d54c1fa)

## Как запустить сайт у себя на компьютере
* Запустите app_runner.py
* Запустите api_runner.py
* Зайдите на http://localhost:8080/

## Screenshots
![Скриншот один](misschedule/static/img/screenshots/project-main-page-fhd.png "Project-main-page")

<<<<<<< Updated upstream
![Скриншот один](misschedule/static/img/screenshots/main-page-fhd.png "main-page")
=======
![Скриншот один](misschedule/static/img/screenshots/main-page-fhd.png "main-page")
#
Сайт доступен в интернете [по ссылке](http://ec2-18-196-114-33.eu-central-1.compute.amazonaws.com/)

#  
*Version 1.4*