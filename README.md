## API Behaviour
- `GET /users/:id` returns **404** when a user is not found.
- All responses include a `created_at` timestamp field.
- Authentication uses **JWT bearer tokens** checked on every request.
- Rate limiting returns **429** after 100 requests per minute.
