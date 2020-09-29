import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { Context } from "../context";

export default function Searchbar() {
  const context = useContext(Context);
  const { searchQuery, handleChange } = context;

  return (
    <div>
      <label htmlFor="searchQuery">Search products:</label>
      <input
        type="text"
        id="searchQuery"
        name="searchQuery"
        value={searchQuery}
        onChange={handleChange}
      />
      <Link to={`/recommendations/${searchQuery}`}>Search...</Link>
    </div>
  );
}
