set -a
source .env
set +a

cd terraform

export TF_VAR_project=$PROJECT
export TF_VAR_bucket=$BUCKET
export TF_VAR_dataset=$DATASET
export TF_VAR_project_location=$PROJECT_LOCATION
export GOOGLE_APPLICATION_CREDENTIALS=$LOCAL_GCS_JSON_CREDENTIALS_PATH

terraform init
terraform apply --auto-approve

cd ..

mkdir -p spark/ airflow/logs airflow/dags dbt/
sudo chown -R $(id -u):0 spark/ airflow/logs airflow/dags dbt/
chmod -R 775 spark/ airflow/logs airflow/dags dbt/
docker compose up -d

echo -e "\n"

echo -n "Waiting for Airflow UI"
until curl -s -o /dev/null localhost:8080; do
    echo -n "."
    sleep 5
done
echo " Done!"

echo -e "\n\nAirflow is UP!"

echo -e "\nExpose port 8082 and visit http://localhost:8082/ for dbt docs."
echo -e "Expose port 8501 and visit http://localhost:8501/ for streamlit."
echo -e "Expose port 4040 and visit http://localhost:4040/ for spark web UI."
echo -e "Expose port 8080 and visit http://localhost:8080/ for airflow UI."

# Extract and pretty-print Airflow credentials
creds=$(docker exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated)
echo "Airflow credentials:"
echo "user: $(echo $creds | jq -r 'keys[0]')"
echo "password: $(echo $creds | jq -r '.[keys[0]]')"