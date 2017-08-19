import React from 'react'
import { Form } from 'semantic-ui-react'

export default class RPCCallForm extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      serviceName: 'echo',
      methodName: 'hello',
      paramsJSON: '{}',
      paramsJSONValid: true,
      calls: {},
    }

    this.handleChange = (event, { name, value }) => {
      this.setState({ [name]: value });
      if (name == 'paramsJSON') {
        var valid = true;
        try {
          JSON.parse(value);
        } catch (err) {
          if (window.console) {
            console.debug('JSON parse error:' + err);
          }
          valid = false;
        }
        this.setState({ paramsJSONValid: valid });
      }
    };

    this.handleSubmit = () => {
      const { serviceName, methodName, paramsJSON } = this.state;
      const params = JSON.parse(paramsJSON);
      this.props.handleSubmit({ serviceName, methodName, params });
    }
  }

  render() {
    const { serviceName, methodName, paramsJSON, paramsJSONValid } = this.state;
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Group widths='equal'>
          <Form.Input
            id='input-service-name'
            label='Service name'
            placeholder='Service name'
            name='serviceName'
            value={serviceName}
            onChange={this.handleChange}
          />
          <Form.Input
            id='input-method-name'
            label='Method name'
            placeholder='Method name'
            name='methodName'
            value={methodName}
            onChange={this.handleChange}
          />
        </Form.Group>
        <Form.TextArea
          id='input-params'
          label='Params (JSON)'
          placeholder='{}'
          name='paramsJSON'
          value={paramsJSON}
          onChange={this.handleChange}
          error={!paramsJSONValid}
        />
        <Form.Button
          content="Submit"
          disabled={!paramsJSONValid || !methodName || !serviceName}
          icon='play' labelPosition='left'
          color='red'
        />
      </Form>
    );
  }

}
