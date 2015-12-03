# Web2py redirector
An easy to use [web2py][] redirection application.

Originally intended to be placed behind a reverse proxy that handles a part of the URL rewriting from the outside.
This web2py app needs to be adapted so it can work standalone as well. 

Copyright 2015 by Remco Boerma. 
The LGPLv3 is applied to this work, see [LICENSE](LICENSE)

## Installation 
 1. Install [web2py]
 1. Install this app into web2py using the [admin interface][]
 1. copy the `examples\routes.parameteric.example.py` to `routes.py` in the main web2py folder
 1. Add the domains dictionary with the domain you wish to use (`localhost` is assumed here) as a key 
    and the application name as it's value. See the web2py router section below for an example. 
 1. Open `http://<domain>/default/edit` to open the edit screen. 
 1. Log in using `admin`, `admin`
 1. Change the password of the admin account
 1. Feast on your achievements

### Web2py router
```python
routers = dict( 
    # base router
    BASE=dict(
        default_application='welcome',
        domains = {'localhost':'w2p_redirector'}
    ),
)
```


## Usage 

  

 [web2py]: http://www.web2py.com  
 [admin interface]: http://localhost:8000/admin