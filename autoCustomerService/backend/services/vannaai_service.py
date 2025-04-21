import vanna
from vanna.remote import VannaDefault
vn = VannaDefault(model='chinook', api_key=vanna.get_api_key('my-email@example.com'))
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
vn.ask("What are the top 10 albums by sales?")


from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run()

