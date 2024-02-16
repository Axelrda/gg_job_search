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

# gcloud compute instances create ggjobsearch-vm \
#     --project=ggjobsearch \
#     --zone=us-central1-c \
#     --machine-type=n1-highmem-4 \
#     --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
#     --metadata=ssh-keys=axelus:ssh-rsa\ \
# AAAAB3NzaC1yc2EAAAADAQABAAABAQDWWrRvAolKXoUfOoHHSQhWHag\+2g8AOxbkNAvuEyqcmDMDTuAe\+PjO252rtVORot1/C2p\+OVqRCbFqB7JgBLkKfrLymuxuM4HidL1cIfnVdm0jwGneZiL3av0d8dnAS55TWY\+WlXlfK5CSkcGYeSznmuSB12\+p3qQZ5eTB2pXAoQ0UFBUZrJPkubd6LBSqJBVkXqqWBlxF7pt4kf2TeRBMQxqpbBZeB72Jux2M7dZoolz1LbJK5AM6Ju4KfdBAPImB5NEKfa7ifA2Qo3ttbhTjrsNBtOBv4IIyF01o\+mUKN3peO91uOeDam/2aUW\+1DWblvay1I3FVEBNgfzoVs4tJ\ axelus \
#     --no-restart-on-failure \
#     --maintenance-policy=TERMINATE \
#     --provisioning-model=STANDARD \
#     --service-account=365054896223-compute@developer.gserviceaccount.com \
#     --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
#     --accelerator=count=1,type=nvidia-tesla-t4 \
#     --create-disk=auto-delete=yes,boot=yes,device-name=instance-1,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240126,mode=rw,size=30,type=projects/ggjobsearch/zones/us-central1-a/diskTypes/pd-balanced \
#     --no-shielded-secure-boot \
#     --shielded-vtpm \
#     --shielded-integrity-monitoring \
#     --labels=goog-ec-src=vm_add-gcloud \
#     --reservation-affinity=any
    


#     ##### SPOT VERSION WITH DEBIAN DEEP LEARNING GPU OPTIMIZED (CUDA INSTALLED) 
#     gcloud compute instances create ggjobsearch-vm \
#     --project=ggjobsearch \
#     --zone=us-central1-c \
#     --machine-type=n1-highmem-4 \
#     --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
#     --metadata=ssh-keys=axelus:ssh-rsa\ \
# AAAAB3NzaC1yc2EAAAADAQABAAABAQDWWrRvAolKXoUfOoHHSQhWHag\+2g8AOxbkNAvuEyqcmDMDTuAe\+PjO252rtVORot1/C2p\+OVqRCbFqB7JgBLkKfrLymuxuM4HidL1cIfnVdm0jwGneZiL3av0d8dnAS55TWY\+WlXlfK5CSkcGYeSznmuSB12\+p3qQZ5eTB2pXAoQ0UFBUZrJPkubd6LBSqJBVkXqqWBlxF7pt4kf2TeRBMQxqpbBZeB72Jux2M7dZoolz1LbJK5AM6Ju4KfdBAPImB5NEKfa7ifA2Qo3ttbhTjrsNBtOBv4IIyF01o\+mUKN3peO91uOeDam/2aUW\+1DWblvay1I3FVEBNgfzoVs4tJ\ axelus \
#     --no-restart-on-failure \
#     --maintenance-policy=TERMINATE \
#     --provisioning-model=SPOT \
#     --instance-termination-action=STOP \
#     --service-account=365054896223-compute@developer.gserviceaccount.com \
#     --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
#     --accelerator=count=1,type=nvidia-tesla-t4 \
#     --create-disk=auto-delete=yes,boot=yes,device-name=ggjobsearch-vm,image=projects/ml-images/global/images/c0-deeplearning-common-gpu-v20240111-debian-11-py310,mode=rw,size=50,type=projects/ggjobsearch/zones/us-central1-c/diskTypes/pd-balanced \
#     --no-shielded-secure-boot \
#     --shielded-vtpm \
#     --shielded-integrity-monitoring \
#     --labels=goog-ec-src=vm_add-gcloud \
#     --reservation-affinity=any