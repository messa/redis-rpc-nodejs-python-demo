import React from 'react'
import Link from 'next/link'
import { Container } from 'semantic-ui-react'
import 'isomorphic-fetch'

import CustomHead from '../components/CustomHead'
import RPCCallForm from '../components/RPCCallForm'


const postJSON = async (url, payload) => {
  const res = await fetch(url, {
    method: 'post',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  return await res.json();
};


export default class IndexPage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      calls: {},
    };
  }

  handleCallSubmit({ serviceName, methodName, params }) {
    const callId = 'c' + new Date() * 1;
    const callState = {
      serviceName, methodName, params,
      startDate: new Date(),
      inProgress: true,
      result: null,
      error: null,
    };
    this.setState(state => ({ calls: {  ...state.calls, [callId]: callState } }));
    this.performCall({ callId, serviceName, methodName, params });
  }

  async performCall({ callId, serviceName, methodName, params }) {
    var callStateUpdate = {};
    try {
      const data = await postJSON('/api/performCall', { serviceName, methodName, params });
      callStateUpdate = {
        inProgress: false,
        error: null,
        result: data,
      };
    } catch (e) {
      callStateUpdate = {
        inProgress: false,
        error: e.toString(),
      };
    }
    this.setState(state => ({ calls: { ...state.calls, [callId]: { ...state.calls[callId], ...callStateUpdate } } }));
  }

  render() {
    const { calls } = this.state;
    return (
      <div className="pageContainer">
        <CustomHead />
        <Container text>
          <h1>Redis RPC demo</h1>
          <RPCCallForm
            handleSubmit={(data) => this.handleCallSubmit(data)}
          />
          {!calls ? null : (
            <section>
              <h2>RPC calls</h2>
              <pre>{JSON.stringify(calls, null, 2)}</pre>
            </section>
          )}
        </Container>
      </div>
    );
  }
}
