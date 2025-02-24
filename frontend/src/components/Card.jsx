import React from 'react'

export default function Card({ data }) {
  console.log({ data })
  const { columns, rows } = data

  return (

    <div className='p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-100'>
      {
        columns?.map((item, index) => {
          return (
            <div key={index}>
              <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 ">{item}</h5>
            </div>
          )
        })
      }

      {
        rows?.map((item, index) => {
          return (
            <div key={index}>
              <p className="font-normal text-gray-700 dark:text-gray-400">{item}</p>
            </div>
          )
        })
      }
    </div>

  )
}
