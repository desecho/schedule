The web application on Python2/Django/jQuery/AngularJS.
Creates a schedule for learning centers.

##Required packages

* [Python v2.6.5+](http://www.python.org)
* [Django v1.5](http://djangoproject.com)
* [django-annoying v0.7.7+](https://github.com/skorokithakis/django-annoying)
* [pyhunspell v0.1](https://code.google.com/p/pyhunspell/)
* [CoffeeScript v1.6.1](http://coffeescript.org)

##Used Javascript libraries
* [jQuery v1.9.1](http://jquery.com/)
* [jGrowl v1.2.11](https://github.com/stanlemon/jGrowl)
* [Spin.js v1.2.8](http://fgnass.github.com/spin.js/)
* [jQuery Plugin for Spin.js](https://gist.github.com/its-florida/1290439/)
* [Bootstrap v2.3.1](http://twitter.github.com/bootstrap/)

##Installation instructions

* Change the following variables in settings.py:
    * DATABASES

* Run
```
python manage.py syncdb
python manage.py collectstatic
```
