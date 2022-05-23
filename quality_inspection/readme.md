## 印章标注规范检查
1. 整张图片包含多个印章的数据格式检查脚本
   ```
   $ cd quality_inspection
   $ python mutil_img.py -i path
   ```
   `path`替换为本机标注目录地址  
   目录下文件格式为：
   ```
   path/ 
        1/  
        1.json
        2/  
        2.json
        ...
    ```
2. 单张印章标注的数据格式检查脚本
    ```
    $ cd quality_inspection
    $ python signal_img.py -i path
    ```
    `path`替换为本机标注目录地址   
    目录下文件格式为：
    ```
    path/ 
            1/  
            1.json
            2/  
            2.json
            ...
    ```


### 都完成且没有问题之后再用下面的脚本确认
3. 单张印章标注的数据处理成可用格式
    ```
    $ cd quality_inspection
    $ python signal_seal_process.py -i path
    ```
    `path`替换为本机标注目录地址   
    目录下文件格式为：
    ```
    path/ 
            1/  
            1.json
            2/  
            2.json
            ...
    ```

4. 整张图片包含多个印章的数据处理成可用格式
    ```
    $ cd quality_inspection
    $ python mutil_seal_process.py -i path
    ```
    `path`替换为本机标注目录地址   
    目录下文件格式为：
    ```
    path/ 
            1/  
            1.json
            2/  
            2.json
            ...
    ```

5. 数量检查工具
    ```
    $ cd quality_inspection
    $ python sum.py -i path -f flag
    ```
    `flag`只能写  `signal` 和 `mutil`  
    - `signal` 表示单张印章标注  
    - `mutil`  表示整张图片包含多个印章标注