# Next time you need to install something with python setup.py -- which should be never but things happen. 

python setup.py install --record files.txt

# This will cause all the installed files to be printed to that directory.
# Then when you want to uninstall it simply run; be careful with the 'sudo'

cat files.txt | xargs sudo rm -rf

rm -rf build
rm -rf dist
rm -rf twitterscraper.egg-info
rm files.txt
