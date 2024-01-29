echo "Creating the GCP VM instance..."

# Create VM instance
gcloud compute instances create $INSTANCE \
    --metadata=ssh-keys="$USERNAME:$(echo $KEY_VALUE)" \
    --project=$PROJECT \
    --zone=$ZONE \
    --image-project=$IMAGE_PROJECT \
    --image-family=$IMAGE_FAMILY \
    --machine-type=$MACHINE_TYPE \
    --accelerator=count=$ACCELERATOR_COUNT,type=$ACCELERATOR_TYPE \
    --boot-disk-size=$BOOT_DISK_SIZE

# Check the exit code of the gcloud command
if [ $? -eq 0 ]; then
    echo "✅ GCP VM instance created"
else
    echo "❌ Error creating GCP VM instance"
fi
