import React, { Component } from "react";

export default class RecommendationPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      slug: this.props.match.params.slug,
    };
  }
  render() {
    return <div>Recommendations page: {this.state.slug}</div>;
  }
}
