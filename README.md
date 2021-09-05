# foody-backend
This is my playground project where I integrate new things which I've been learning in order to get a better experience. 
The project consists of the backend written on Django and a native [android application](https://github.com/AlieksieievYurii/foody-application). 
The project itself is a food order service.

# Overview
This is a backend for the food delivery service, implemented by Django + DRF. Moreover, the backend uses other external services:
* [Cloudunary](https://cloudinary.com/)
* [Mailgun](https://www.mailgun.com/)

# Installation
Python => 3.9 is required.

First of all, you need to install the requirements.

```python install -r requirements.txt```

Once you done it, you need to create `.env` file and specify the following variables:
```
#General
DEBUG=on
SECRET_KEY=<secret-key>

# MailGun
MAILGUN_API_KEY=<mailgun-api-key>
MAILGUN_DOMAIN_NAME=<mailgun-domain-name>

#Cloudinary
CLOUDINARY_CLOUD_NAME=<cloudinary-cloud-name>
CLOUDINARY_API_KEY=<cloudinary-api-key>
CLOUDINARY_API_SECRET=<cloudinary-api-sectet>
```
Note: intead of the syntax `<...>` must be your values.

# Start the backend
Once you have done all necessary things, you can run:
`py manage.py runserver`
