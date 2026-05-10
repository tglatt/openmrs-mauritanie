FROM openmrs/openmrs-reference-application-3-backend:3.6.0

USER root
RUN rm -rf /openmrs/distribution/openmrs_config/*
USER 1001
