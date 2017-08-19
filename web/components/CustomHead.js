import Head from 'next/head'

const style = `

  body {
    background: #f9f9f9;
  }

  body, html {
    height: inherit;
  }

  pre {
    font-size: 13px;
    font-family: Inconsolata, monospace;
    line-height: 1.25;
  }

  h1, h1:first-child,
  h2, h2:first-child {
    margin-top: 2rem;
    margin-bottom: 1rem;
  }

`;

export default () => {
  return (
    <Head>
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
      <title>Redis RPC demo</title>
      <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.11/semantic.min.css" />
      <style>{style}</style>
    </Head>
  );
};
