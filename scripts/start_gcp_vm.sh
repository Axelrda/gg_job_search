echo "Starting the GCP VM instance..."

# Start the instance
gcloud compute instances start $INSTANCE --zone=$ZONE
