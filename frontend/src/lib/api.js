async function request(path, options = {}) {
  const { headers: rawHeaders, ...restOptions } = options
  const headers = rawHeaders === null
    ? {}
    : {
        'Content-Type': 'application/json',
        ...(rawHeaders || {}),
      }
  const response = await fetch(path, {
    ...restOptions,
    headers,
  })

  if (!response.ok) {
    let message = `请求失败（${response.status}）`
    try {
      const data = await response.json()
      message = data.detail || data.message || message
    } catch {
      // ignore
    }
    throw new Error(message)
  }

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

export const api = {
  get(path) {
    return request(path)
  },
  post(path, body) {
    return request(path, {
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
      headers: body instanceof FormData ? null : undefined,
    })
  },
  put(path, body) {
    return request(path, {
      method: 'PUT',
      body: JSON.stringify(body ?? {}),
    })
  },
  delete(path) {
    return request(path, { method: 'DELETE' })
  },
}
