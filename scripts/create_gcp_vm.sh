echo "Creating the GCP VM instance..."

# Create VM instance
gcloud compute instances create $VM_INSTANCE \
    --metadata=ssh-keys="$VM_USERNAME:$(echo $SSH_KEY_VALUE)" \
    --project=$GCP_PROJECT \
    --zone=$GCP_ZONE \
    --image-project=$IMAGE_PROJECT \
    --image-family=$IMAGE_FAMILY \
    --machine-type=$MACHINE_TYPE \
    --boot-disk-size=$BOOT_DISK_SIZE
    #--accelerator=count=$ACCELERATOR_COUNT,type=$ACCELERATOR_TYPE \

# Check the exit code of the gcloud command
if [ $? -eq 0 ]; then
    echo "✅ GCP VM instance created"
else
    echo "❌ Error creating GCP VM instance"
fi
