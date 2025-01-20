# Kubernetes Deployment Guide

This guide explains how to deploy the **Datacatalog** using **MicroK8s** and **Helm**.

---

## Prerequisites

1. **MicroK8s**: A lightweight Kubernetes distribution.
2. **Helm**: A package manager for Kubernetes (already included in MicroK8s).

---

## Deployment Steps

### 1. Install MicroK8s

To install MicroK8s, run the following command:

```bash
sudo snap install microk8s --classic
```

### 2. Enable Required MicroK8s Add-ons

Enable the necessary MicroK8s add-ons for DNS, ingress, and Helm:

```bash
microk8s enable dns ingress helm3
```

### 3. Configure the `values.yaml` File

Before deploying the **Datacatalog**, update the `values.yaml` file with your Keycloak configuration details for authentication. Here’s an example:

```yaml
backend:
  authentication: "true"
  keycloak:
    authUrl: "https://keycloak.example.com"
    realm: "your-realm"
    clientId: "your-client-id"
    clientSecret: "your-client-secret"
```

- Replace `https://keycloak.example.com` with your Keycloak server URL.
- Replace `your-realm`, `your-client-id`, and `your-client-secret` with your actual Keycloak configuration.

### 4. Deploy the Application

Navigate to the directory containing your Helm chart and deploy the **Datacatalog** using:

```bash
microk8s helm3 install datacatalog .
```

Here:
- `datacatalog` is the release name for your deployment.
- `.` refers to the current directory containing the Helm chart.