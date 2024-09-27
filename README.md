
## Requirements

- **Ubuntu**: This application requires Ubuntu to run. Ensure you are using an Ubuntu environment for optimal performance.
- **Daphne**: The ASGI server for Django (must be installed).

## Running the ASGI Application with Daphne

To run the Django ASGI application using Daphne, use the following command:

```bash
daphne -b 0.0.0.0 -p 8000 miniblog.asgi:application
