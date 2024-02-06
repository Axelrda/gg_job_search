gcloud compute resource-policies create instance-schedule $INSTANCE_SCHEDULE \
    --description=$SCHEDULE_DESCRIPTION \
    --vm-start-schedule=$START_OPERATION_SCHEDULE \
    --vm-stop-schedule=$STOP_OPERATION_SCHEDULE \
    #[--region=] \
    #[--timezone=$TIME_ZONE] \
    #[--initiation-date=] \
    #[--end-date=]
