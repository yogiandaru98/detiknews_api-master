from dn_scraper import DetikNewsScraper
from flask import Flask, jsonify, request
import time
import logging

app = Flask(__name__)

# Initialize the DetikNewsScraper object
DN_API = DetikNewsScraper()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/search", methods=["GET"])
def search():
    """Endpoint untuk pencarian berita Detik dengan dukungan multi-halaman"""
    try:
        # Retrieve parameters with defaults
        params = {
            "query": request.args.get("q", default="", type=str),
            "page": request.args.get("page", default=1, type=int),
            "pages": request.args.get("pages", default=1, type=int),
            "detail": request.args.get("detail", default="false", type=str).lower() in ["true", "1"],
            "limit": request.args.get("limit", default=None, type=int),
            "delay": request.args.get("delay", default=2.0, type=float)
        }

        # Validate required parameters
        if not params["query"]:
            return jsonify({
                "status": 400,
                "error": "Parameter 'q' (query) diperlukan",
                "example": "/search?q=politik&pages=2&detail=true"
            }), 400

        # Validate numeric parameters
        if params["page"] < 1 or params["pages"] < 1:
            return jsonify({
                "status": 400,
                "error": "Parameter 'page' dan 'pages' harus lebih besar dari 0"
            }), 400

        if params["delay"] < 0:
            return jsonify({
                "status": 400,
                "error": "Parameter 'delay' tidak boleh negatif"
            }), 400

        logger.info(f"Memproses pencarian: {params}")

        # Perform multi-page search
        all_results = []
        current_page = params["page"]
        end_page = current_page + params["pages"] - 1
        
        while current_page <= end_page:
            try:
                # Get results for current page
                page_results = DN_API.search(
                    query=params["query"],
                    page_number=current_page,
                    detail=params["detail"],
                    limit=params["limit"]
                )
                
                if not page_results:
                    logger.info(f"Tidak ada hasil di halaman {current_page}")
                    break
                    
                all_results.extend(page_results)
                
                # Check if we've reached our limit
                if params["limit"] is not None and len(all_results) >= params["limit"]:
                    all_results = all_results[:params["limit"]]
                    break
                    
                # Move to next page
                current_page += 1
                
                # Respectful delay between requests
                time.sleep(params["delay"])
                
            except Exception as e:
                logger.error(f"Error saat scraping halaman {current_page}: {str(e)}")
                break

        return jsonify({
            "status": 200,
            "parameters": params,
            "data": all_results,
            "count": len(all_results),
            "pages_scraped": current_page - params["page"],
            "message": "Berhasil mengambil data" if all_results else "Tidak ada hasil ditemukan"
        }), 200

    except Exception as e:
        logger.error(f"Error dalam pencarian: {str(e)}", exc_info=True)
        return jsonify({
            "status": 500,
            "error": "Terjadi kesalahan internal",
            "details": str(e)
        }), 500

@app.route("/", methods=["GET"])
def home():
    """Endpoint utama dengan dokumentasi API"""
    return jsonify({
        "status": 200,
        "message": "Detik News Scraper API",
        "endpoints": {
            "/search": {
                "description": "Pencarian berita Detik",
                "parameters": {
                    "q": "Kata kunci pencarian (wajib)",
                    "page": "Halaman mulai (default: 1)",
                    "pages": "Jumlah halaman yang akan discrape (default: 1)",
                    "detail": "Ambil konten lengkap (true/false, default: false)",
                    "limit": "Batas maksimal hasil (default: semua)",
                    "delay": "Delay antar request dalam detik (default: 2.0)"
                },
                "example": "/search?q=pemilu&pages=2&detail=true&limit=20"
            }
        }
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)