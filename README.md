## Running the ASGI Application with Daphne

To run the Django ASGI application using Daphne, use the following command:

```bash
daphne -b 0.0.0.0 -p 8000 miniblog.asgi:application
