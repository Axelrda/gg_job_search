# Empty ssh config file
echo -n > ~/.ssh/config

# set upp ssh config file
gcloud compute config-ssh --force-key-file-overwrite


# echo "Retrieving the new external IP address of the instance..."
# # Get the external IP of the instance
# NEW_EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE \
#          --zone=$ZONE \
#          --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

# echo "New external IP address acquired: $NEW_EXTERNAL_IP"

# echo "Updating the SSH config file..."
# # Update the SSH config file
# sed -i "/Host $HOST_ALIAS/,+3 s/HostName .*/HostName $NEW_EXTERNAL_IP/" $SSH_CONFIG_FILE

# echo "SSH config file has been updated."

# # Change perrmissions of private key --> only accessible (rw) by user
# chmod 600 ~/.ssh/ggjobsearch-gcp-ssh
