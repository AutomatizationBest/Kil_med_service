import axios from 'axios';
import React, { useState } from 'react';
import img from '../media/file-upload.png';

function Dogovor() {
  const [value, setValue]=useState("");

  return (
    <div className='kp'>
      <a name='rzn'/>
      <h1 className='name'>Заполнение договора</h1>
    <div className="main">
      <div className='about'>
        <h1>Договор на мед оборудования</h1>
        <h1>Поиск по реестру Росздравнадзора. По коду товара из предлагаемого оборудования ищется: РУ, Страна производителя, Производитель, ОКПД, полное наименование товара и вариант исполнения.</h1>
      </div>
        <form action='#' className='excel'>
          <div className='dnd'>
            <div className="droparea">
              <img src={img}/>
            </div>
            <input 
              multiple='false'
              name='file' 
              type='file' 
              accept='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
              className='addfile'
              onChange={(e)=>{setValue(e.target.files[0])
              }}/>
            </div>
            <button 
              type='submit' 
              className='send'
              onClick={()=>{
                const formData= new FormData()
                formData.append('file',value)
                const user1 = axios.post("http://localhost:8000/kp",formData,{ responseType: 'blob' })
                .then(res=>{
                  console.log(res.data)
                  
                  const blob= new Blob([res.data])
                  const url = window.URL.createObjectURL(blob);

                  let anchor =document.createElement('a');
                  anchor.href=url;
                  anchor.download='dog.xlsx';
                  document.body.append(anchor);
                  anchor.style="display : none";
                  anchor.click();
                  anchor.remove();


                  window.URL.revokeObjectURL(url)
                })
                .catch(error=>{
                  console.error(error)
                });

                // const user= axios.get("http://localhost:8000").then(response =>{
                //   console.log(response.data);
                // }).catch(error=>{
                //   console.error(error)
                // });
                // console.log(user.headers);
              }}>Отправить</button>
        </form>
        {/* <button className='send'>Отправить</button> */}
    </div>
    <div className="example">
      <h1 className='name'>Необходимые заполненные столбцы</h1>
      <table border='1' cellSpacing='0' cellPadding="10">
      <tr>
          <th>Наименование предлагаемого оборудования</th>
          <th>Производитель</th>
          <th>Страна происхождения</th>
        </tr>
        <tr>
          <th>Моечно-дезинфицирующий автоматический репроцессор для гибких эндоскопов марки Detro Wash 8005</th>
          <th>ООО "МЕДЕЛИЯ"</th>
          <th>Россия</th>
        </tr>
        <tr>
          <th>...</th>
          <th>...</th>
          <th>...</th>
        </tr>
      </table>
    </div>
    </div>
  );
}

export default Dogovor;
