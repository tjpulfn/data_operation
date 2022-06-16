# data_operation

- 数据操作
  - 
  - #### 数据转换
    ```
    $ cd data_transcription
    ```
  - ##### 将使用vgg标注的文件转换成labelme标注（后续应该不会使用）

    ```
    $ python tolabelme.py
    ```
  - ##### labelme标注格式的印章，直接转换成可训练使用的格式
    ```
    $ python seal_data2train.py -i input_path  -rn 0
    ```

  - 