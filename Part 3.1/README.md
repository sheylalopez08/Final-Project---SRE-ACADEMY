# Guía Completa: Ansible + Minikube + Infraestructura como Código

Este documento resume **todo lo que hemos trabajado y solucionado** sobre Ansible, incluyendo:
- Configuración del inventario
- Problemas con rutas y espacios
- Errores comunes y cómo los resolvimos
- Uso de entornos virtuales (venv)
- Ejecución de playbooks
- Despliegue de aplicación Flask en Minikube
- Validación del entorno
- Creación de un playbook IaC para automatizar infraestructura

---

## 1. **Configuración del Inventario**

Para que Ansible use el intérprete de Python correcto (venv), configuramos `inventory.ini`:

```ini
[local]
localhost ansible_connection=local ansible_python_interpreter="/Users/sheyla.lopez/Documents/FINAL PROJECT - SRE ACADEMY/Final Project /My Cellphone App/Part 1/venv/bin/python"
```

### ✅ Problemas encontrados:
- **Espacios en la ruta**: Ansible fallaba incluso con comillas.
- **Error**: `No closing quotation` → causado por comillas mal cerradas.
- **Error**: `hostname contains invalid characters` → cuando se pasó la ruta como host.

### ✅ Solución:
- Usar comillas correctamente.
- Confirmar la ruta real del venv con:
```bash
which python
python -c "import sys; print(sys.executable)"
```

---

## 2. **Errores comunes y soluciones**

### ❌ `No such file or directory`
Causa: Ruta incorrecta del venv.
Solución: Verificar con `ls` y corregir en el inventario.

### ❌ `Could not match supplied host pattern`
Causa: Usar `local` cuando el inventario define `localhost`.
Solución:
```bash
ansible -i inventory.ini localhost -m ping
```

### ❌ `MaxRetryError: HTTPSConnectionPool`
Causa: Minikube no estaba corriendo.
Solución:
```bash
minikube start
minikube status
```

---

## 3. **Playbook para despliegue Flask en Minikube**

Creamos un playbook que:
- Inicia Minikube
- Carga imagen Docker
- Aplica Deployment y Service
- Valida rollout y muestra pods y servicios

Ejemplo:
```yaml
- name: Desplegar aplicación Flask en Minikube
  hosts: localhost
  connection: local
  gather_facts: yes

  vars:
    namespace: "my-cellphone"
    kubeconfig_path: "{{ lookup('env', 'HOME') + '/.kube/config' }}"
    image_name: "my-cellphone-app:tag"
    deployment_path: "/ruta/deployment.yaml"
    service_path: "/ruta/service.yaml"

  tasks:
    - name: Iniciar Minikube
      ansible.builtin.command: minikube start
    - name: Aplicar Deployment
      kubernetes.core.k8s:
        state: present
        kubeconfig: "{{ kubeconfig_path }}"
        namespace: "{{ namespace }}"
        src: "{{ deployment_path }}"
```

### ✅ Validación:
```bash
kubectl get pods -n my-cellphone
kubectl get svc -n my-cellphone
minikube service my-cellphone-svc -n my-cellphone
```

---

## 4. **Playbook IaC (iac_playbook.yaml)**

Este playbook automatiza:
- Instalación de Minikube y Podman
- Inicio de servicios
- Soporte para macOS y Linux

Ejemplo:
```yaml
- name: Infraestructura como Código - Configuración completa
  hosts: localhost
  connection: local
  gather_facts: yes

  tasks:
    - name: Detectar sistema operativo
      ansible.builtin.debug:
        msg: "Sistema operativo detectado: {{ ansible_facts['os_family'] }}"
    - name: Instalar paquetes en macOS
      ansible.builtin.homebrew:
        name: "{{ item }}"
        state: present
      loop:
        - minikube
        - podman
```

---

## 5. **Buenas prácticas**
- Evitar espacios en rutas (renombrar carpetas si es posible).
- Usar `ansible.cfg` para definir `interpreter_python` globalmente.
- Validar Minikube antes de aplicar recursos.
- Instalar dependencias de Kubernetes en el venv:
```bash
pip install kubernetes openshift
```

---

## 6. **Comandos útiles**
```bash
ansible -i inventory.ini localhost -m ping
ansible-playbook playbook.yaml -i inventory.ini
ansible-playbook iac_playbook.yaml -i inventory.ini
```

---

### ✅ Resultado final
- Inventario configurado correctamente.
- venv funcionando con Ansible.
- Playbook de despliegue Flask operativo.
- Playbook IaC listo para automatizar infraestructura.

