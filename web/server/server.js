const express = require('express')
const next = require('next')

import cookieParser from 'cookie-parser'
import bodyParser from 'body-parser'
import session from 'express-session'

import api from './api'

const port = parseInt(process.env.PORT, 10) || 3000
const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()

app.prepare()
.then(() => {
  const server = express()

  server.use(cookieParser())
  server.use(bodyParser.urlencoded({ extended: true }))
  server.use(bodyParser.json())
  server.use(session({
    secret: 'topsecret',
    resave: false,
    saveUninitialized: true,
  }))

  server.use('/api', api);

  server.get('*', (req, res) => {
    return handle(req, res)
  })

  server.listen(port, (err) => {
    if (err) throw err
    console.log(`> Ready on http://localhost:${port}`)
  })
})
