import React from "react";
import { Switch, Route } from "react-router-dom";
import "./App.css";

import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import RecommendationPage from "./pages/RecommendationPage";
import StatsPage from "./pages/StatsPage";
import AboutPage from "./pages/AboutPage";
import ErrorPage from "./pages/ErrorPage";

function App() {
  return (
    <>
      <Navbar />
      <Switch>
        <Route exact path="/" component={HomePage} />
        <Route
          exact
          path="/recommendations/:slug"
          component={RecommendationPage}
        />
        <Route exact path="/stats/" component={StatsPage} />
        <Route exact path="/about/" component={AboutPage} />
        <Route component={ErrorPage} />
      </Switch>
    </>
  );
}

export default App;
