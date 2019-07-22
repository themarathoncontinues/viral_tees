source /home/envs/vt/bin/activate
source /home/git/viral_tees/.env

export PYTHONPATH=/home/git/viral_tees/

python /home/git/viral_tees/run_luigi.py --all --soft 

deactivate
