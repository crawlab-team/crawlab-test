const axios = require('axios')
const fs = require('fs')
const path = require('path')

const endpoint = 'http://localhost:8000'

const getToken = async () => {
  const username = 'admin'
  const password = 'admin'
  const res = await axios.post(`${endpoint}/login`, {
    username,
    password
  }, {
    headers: {
      'Content-Type': 'application/json',
    }
  })
  return res.data.data
}

const createSpider = async (spider, token) => {
  return await axios.put(`${endpoint}/spiders`, spider, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token,
    }
  })
}

const uploadSpiderFile = async (_id, token) => {
  const filePath = path.resolve(path.join(__dirname, 'template', 'main.py'))
  const file = fs.readFileSync(filePath)
  const data = file.toString()
  await axios.post(`${endpoint}/spiders/${_id}/files/save`, {
    path: 'main.py',
    data,
  }, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token,
    },
  })
}

const runSpider = async (_id, token) => {
  return await axios.post(`${endpoint}/spiders/${_id}/run`, {
    priority: Math.floor(Math.random() * 10 + 1),
    mode: 'random',
  }, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token,
    },
  })
}

(async () => {
  // settings
  const spiderNum = 50
  const tasksPerSpider = 10

  // token
  const token = await getToken()

  // spider ids
  const spiderIds = []

  // create spiders
  for (let i = 0; i < spiderNum; i++) {
    const now = new Date().getTime()
    const random = Math.floor(Math.random() * 1e3)
    const name = `spider_${now}_${random}`
    const res = await createSpider({
      name,
      col_name: `results_${name}`,
      cmd: 'python3 main.py',
      mode: 'random',
    }, token)
    const _id = res.data.data._id
    spiderIds.push(_id)
  }

  // upload spider files
  for (let i = 0; i < spiderNum; i++) {
    const _id = spiderIds[i]
    await uploadSpiderFile(_id, token)
    await new Promise(resolve => setTimeout(resolve, 100))
  }

  // run spider tasks
  for (let i = 0; i < spiderNum; i++) {
    const _id = spiderIds[i]
    for (let j = 0; j < tasksPerSpider; j++) {
      await runSpider(_id, token)
    }
  }
})()
