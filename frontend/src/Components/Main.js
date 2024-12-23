import axios from 'axios';
import React, { useState } from 'react';
import img from '../media/file-upload.png';

function Main() {
  const [value, setValue]=useState("");

  return (
    <div className='kp'>
      <a name='kp'/>
      <h1 className='name'>Заполнение КП</h1>
    <div className="main">
      <div className='about'>
        <h1>Добро пожаловать на сайт для быстрого форматирования файлов</h1>
        <h1>Lorem ipsum dolor sit amet consectetur adipisicing elit. Libero doloremque doloribus optio voluptate sapiente est culpa praesentium alias eius, perferendis laboriosam unde accusamus, dignissimos corrupti quibusdam, odio ipsa! Enim, pariatur.</h1>
      </div>
        <form action='#' className='excel'>
           <div className='dnd'>
            <div className="droparea">
              <img src={img}/>
            </div>
            <input 
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
                const user1 = axios.post("http://localhost:8000",formData,{ responseType: 'blob' })
                .then(res=>{
                  console.log(res.data)
                  
                  const blob= new Blob([res.data])
                  const url = window.URL.createObjectURL(blob);

                  let anchor =document.createElement('a');
                  anchor.href=url;
                  anchor.download='img.xlsx';
                  document.body.append(anchor);
                  anchor.style="display : none";
                  anchor.click();
                  anchor.remove();


                  window.URL.revokeObjectURL(url)
                })
                .catch(error=>{
                  console.error(error)
                });
              }}>Отправить</button>
        </form>
    </div>
    <div className="example">
      <h1 className='name'>Необходимые заполненные столбцы</h1>
      <table border='1' cellSpacing='0' cellPadding="10">
        <tr>
          <th>№пп</th>
          <th>Наименование оборудования (оснащения)</th>
          <th>Технические характеристики из запроса</th>
          <th>Кол-во</th>
          <th>Наименование от ГМК Киль</th>
          <th>Технические характеристики предлагаемого оборудования</th>
          <th>Примечание</th>
          <th>Цена продажи</th>
          <th>Стоимость</th>
          <th>Ставка НДС</th>
        </tr>
        <tr>
          <th>47</th>
          <th>Емкости для сбора бытовых и медицинских отходов</th>
          <th>"Материал изделия-полипропилен
Фактический объем изделия-35 л
Высота изделия 40 см
Верхний диаметр-40 ем
Нижний диаметр-29,5 см"</th>
          <th>2</th>
          <th>Бак п/э с крышкой 35 л </th>
          <th>"Материал изделия-полипропилен
Фактический объем изделия-35 л
Высота изделия 40 см
Верхний диаметр-40 ем
Нижний диаметр-29,5 см"</th>
          <th>Ошибка вТХ</th>
          <th> 960,00 </th>
          <th> 1 920,00   </th>
          <th>10%</th>
        </tr>
        <tr>
          <th>...</th>
          <th>...</th>
          <th>...</th>
          <th>...</th>
          <th>...</th>
          <th>...</th>
          <th>...</th>
          <th>...</th>
          <th>...</th>
          <th>...</th>
        </tr>
      </table>
    </div>
    </div>
  );
}

export default Main;
