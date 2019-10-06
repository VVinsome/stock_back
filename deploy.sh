
# build our heroku-ready local Docker image
docker build -t stock-back-api -f Dockerfile .

#login to heroku docker
heroku container:login
# push your directory container for the web process to heroku
heroku container:push web -a stock-back-api


# promote the web process with your container 
heroku container:release web -a stock-back-api


# run migrations
heroku run python3 manage.py migrate -a stock-back-api