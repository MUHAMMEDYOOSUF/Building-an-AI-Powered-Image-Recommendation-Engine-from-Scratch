import React, { useState, useEffect } from "react";
import axios from "axios";
import "./SearchPage.css";

type DataDict = {
  image: string;
  Category: string;
  Colour: string;
  Gender: string;
  Image: string;
  ProductId: number;
  ProductTitle: string;
  ProductType: string;
  SubCategory: string;
  Usage: string;
};

const SearchPage: React.FC = () => {
  const [searchType, setSearchType] = useState<string>("image");
  const [query, setQuery] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [resultData, setData] = useState<DataDict[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleSearchTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchType(e.target.value);
    setImagePreview(null); // reset image preview when search type changes
    setFile(null);
  };

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      const fileURL = URL.createObjectURL(e.target.files[0]);
      setImagePreview(fileURL); // Set image preview
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      let response;
      if (searchType === "image" && file) {
        const formData = new FormData();
        formData.append("file", file);

        response = await axios.post("http://localhost:8000/search_by_image/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else if (searchType === "query") {
        response = await axios.post("http://localhost:8000/search_by_query/", { query });
      }

      if (response && response?.data) {
        setData(response?.data?.results);
      }
    } catch (error) {
      console.error("Error searching:", error);
    }
    setLoading(false);
  };

  return (
    <div className="main-container">

<div className="search-container">
      <h2>IntelliSearch: AI Image Retrieval Agent</h2>
      <div className="search-options">
        <label>
          <input
            type="radio"
            value="image"
            checked={searchType === "image"}
            onChange={handleSearchTypeChange}
          />
          Search by Image
        </label>
        <label>
          <input
            type="radio"
            value="query"
            checked={searchType === "query"}
            onChange={handleSearchTypeChange}
          />
          Search by Query
        </label>
      </div>

      {searchType === "image" && (
        <div className="image-search">
          <div className="image-upload">
            <label htmlFor="file-upload">Upload Image:</label>
            <input type="file" id="file-upload" onChange={handleFileChange} accept="image/*" />
          </div>
        
        </div>
      )}

      {searchType === "query" && (
        <div className="query-search">
          <label htmlFor="query-input">Search Query:</label>
          <input
            type="text"
            id="query-input"
            value={query}
            onChange={handleQueryChange}
            placeholder="Enter search query"
            className="query-input"
          />
        </div>
      )}

      <button onClick={handleSearch} disabled={loading || (!file && searchType === "image")} className="search-button">
        {loading ? "Searching..." : "Search"}
      </button>

      <div className="results">
        {resultData.length > 0 ? (
          <div className="result-cards">
            <h2 className="image-list-heading">Similar Images</h2>
            {resultData.map((result, index) => (
              <div key={index} className="result-card">
                <img
                  src={`data:image/png;base64,${result.image}`}
                  alt={`Result ${index + 1}`}
                  className="result-image"
                />
                <div className="metadata">
                  <p><strong>Product Title:</strong> {result.ProductTitle}</p>
                  <p><strong>Category:</strong> {result.Category}</p>
                  <p><strong>Subcategory:</strong> {result.SubCategory}</p>
                  <p><strong>Colour:</strong> {result.Colour}</p>
                  <p><strong>Gender:</strong> {result.Gender}</p>
                  <p><strong>Usage:</strong> {result.Usage}</p>
                  <p><strong>Product ID:</strong> {result.ProductId}</p>
                  <p><strong>Product Type:</strong> {result.ProductType}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No results found</p>
        )}
      </div>
    </div>
    <div className="image-preview-card">
  <div className="image-container">
    <h2 className="image-preview-heading">Uploaded Image</h2>
    {imagePreview && <img src={imagePreview} alt="Uploaded" className="preview-image" />}
  </div>
</div>

    </div>
    
  );
};

export default SearchPage;
