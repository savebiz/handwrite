# Specs: API Contracts

- `POST /api/documents/upload`: Multipart file upload -> Returns `DocumentRecord`
- `GET /api/documents/queue`: List records awaiting review / rescan
- `GET /api/documents/{id}`: Fetch single `DocumentRecord` with evidence crops
- `POST /api/documents/{id}/review`: Submit reviewer field decisions (`approved`, `corrected`, `rejected`, `rescan`)
- `GET /api/documents/{id}/export`: Download approved JSON / CSV payload
- `POST /api/evaluation/run`: Trigger baseline vs agent evaluation suite
