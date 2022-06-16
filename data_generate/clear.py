
for i in range(2, 39):
    with open("/Users/liufn/python/data_operation/data_generate/company_files/all_company_{}.txt".format(i)) as fr:
        fr_lines = fr.readlines()
    print(i, len(fr_lines))
    with open("/Users/liufn/python/data_operation/data_generate/company_files/all_company_{}.txt".format(i), "w") as fw:
        for line in fr_lines:
            flage = True
            for char in line:
                if char in "1234567890qazxswedcvfrtgbn·hyujmkiolpQAZ/XSWE—-DCVFRTGB(""“”)（）NHYUJM，、“：KIOLP:：":
                    flage = False
                    break
            if flage:
                fw.write(line)
    with open("/Users/liufn/python/data_operation/data_generate/company_files/all_company_{}.txt".format(i)) as fr:
        fr_lines = fr.readlines()
    print(i, len(fr_lines))