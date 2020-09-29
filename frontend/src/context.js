import React, { Component } from "react";

import commentData from "./testData/commentData";
import submissionData from "./testData/submissionData";
import recommendationData from "./testData/recommendationData";

const Context = React.createContext();

class ContextProvider extends Component {
  state = {
    comments: [],
    submissions: [],
    recommendations: [],
    searchQuery: "",
    loading: true,
  };

  getData = async () => {
    this.setState({
      comments: commentData,
      submissions: submissionData,
      recommendations: recommendationData,
      loading: false,
    });
  };

  componentDidMount() {
    this.getData();
  }

  handleChange = (event) => {
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;
    const name = event.target.name;
    this.setState({
      [name]: value,
    });
  };

  render() {
    return (
      <Context.Provider
        value={{ ...this.state, handleChange: this.handleChange }}
      >
        {this.props.children}
      </Context.Provider>
    );
  }
}

const ContextConsumer = Context.Consumer;

export { Context, ContextProvider, ContextConsumer };
