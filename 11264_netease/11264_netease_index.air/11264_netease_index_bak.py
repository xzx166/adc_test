# -*- encoding=utf8 -*-
from airtest.core.api import *
import time

using("../utility/monitor.air")
from monitor import *

using("../utility/api.air")
from api import *

using("../utility/phase.air")
from phase import *

using("../utility/adc_tools.air")
from adc_tools import *

using("../utility/mask.air")
from mask import *

using("../utility/swipe.air")
from swipe import *

using("../utility/image.air")
from image import *

using("../utility/ocr.air")
from ocr import *


using("../utility/upload.air")
from upload import *

import json
import requests
import os
from PIL import Image


auto_setup(__file__)
ENV = AppEnv.get_instance()

gameName = "永劫无间PC" 
yjwj_eas_map = {}
yjwj_ocr_waiguan_list = []
yjwj_ocr_faxing_list = []
shibieMap = {}

allImages = [
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711088380758-a0f7fbe2-8abc-4610-84cd-b3d7e771bd6c.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1710326384076-5244202e-d49d-48c5-8b41-9ecc4c754ce9.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711088555066-86559d73-be3d-4e29-8d5b-73a84dd96d80.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711089255686-9c860587-d23c-4e1f-86bd-7a537bc4bf58.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711089308210-7432a83a-6b39-4d74-befc-dd56169fb4bd.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090582585-80b2109f-d0e3-4e7b-b715-a55905452ca8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090682735-1db05a14-c5f2-4f55-9a79-01267a63b238.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090712754-7ebbb7b4-4212-45cf-a544-b1873540db18.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090746157-f3ad90ad-f7e8-4e06-a995-8265d25e4f99.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091163838-8c6fe0d5-8201-4241-89b0-fb4b64abd26e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091171837-aeedf176-141e-4414-b532-8f0b2a3555ae.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091176994-1ae7ca30-0885-4d8c-8c1a-70f066c7ab3f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091181988-24396cce-7e8f-4dfb-8873-378ac17a6d3f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091260927-0b775bde-07d6-458c-b015-64cf25bee117.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091265636-60b16178-55fa-4ab0-acb6-c2a52e9acdd1.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091271174-a97c8fb9-f02e-4e08-8f9d-01bae52cad38.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091275888-6a0841cd-ffed-498f-aa99-1b3a5f35724f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091275888-6a0841cd-ffed-498f-aa99-1b3a5f35724f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091307324-aa577e2f-4f85-430d-989d-fbc9a560bce8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091312134-00ab6171-eaa9-42ab-9227-d4976bd573b7.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091317879-544fed2b-c596-458e-a84b-7cf131cdab66.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091326439-f0b9a8cb-7c98-4022-8306-8e6d53834dfd.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091401245-739b7a0a-5435-4117-8a30-981d5b7acf16.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091348121-0637a829-b000-4519-a7e2-b7e1feeac2e2.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091355846-54b2e13b-7b89-4b06-a715-5c48e45e1df7.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091362322-28517a3c-ea9a-468b-9cd2-015a816d832e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091439775-a6e5de7d-84b0-4ef1-94fb-e4ae695cd183.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091421374-70c8d4ca-b55c-4fd9-9764-ba9dc4caa88b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092670021-6620fb69-0818-456b-9311-6aa9d05d3733.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092677104-4fd55399-74a0-4a61-9c2f-dcd7445c6188.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092681253-74f486c1-847e-4193-aa28-654f15f5086f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092687057-d9b278a2-66f9-4c83-bdb7-e125d6e4725f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092693012-aa3f0b10-5ff2-4210-b171-7569dbd210ea.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092697467-539ba517-02d0-41a8-acb5-0b9cd37f5a71.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092944203-504ef51a-cddd-4f59-9ea5-8010919fa0f3.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092885600-5620c66a-b0b9-4d1d-8aba-67c3eb564e39.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093026008-4039ff96-714d-4306-a588-18eee2ff6c12.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093030000-ba4d6170-0b14-492f-98c7-6a964ac7b8f7.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093033814-17492116-3d95-49ed-82e0-56a1ee9d1bd2.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093039371-2fbb429a-714d-4f37-b324-0700c1125b42.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093043577-c25974cf-e733-4ee4-9645-b4eca8bf493d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093051148-4de483ed-1dd1-4bee-a160-fee581919362.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093056648-ecb346b5-2152-4e6b-bd59-40a78a609575.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093062128-da75f34a-774f-403a-b848-53bcbab297c2.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093065686-cacf814c-4f2e-44ec-8b85-62726d758131.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093108685-7618b286-f7b1-45a8-94bd-6f857b25ca5b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093134048-fafc6aab-ae82-4a78-abf8-61b1049c3570.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093139845-2ae934c9-f6a4-4abd-ba39-ec06e28b56f6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093194070-b9915e5b-0af2-4fe0-b6b0-e0e0f469fdca.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093198488-878eb30a-fca7-43e7-ab3a-23234f2564d2.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093202290-93d48cc7-b14f-493a-8ac5-5a1a99bbfc0c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093205914-e8c603af-83ce-4a5b-a1d3-228c3421e8d5.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093209328-cea68ecc-d5d0-4517-b025-8562454cc200.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093213993-d595f629-8e2e-4f7b-a5f4-b94ef1fbc678.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093219816-91d176f0-f219-4d72-98ef-2396d8520a29.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093281476-0f676d11-d6af-4a23-9d60-c0f473695238.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093271598-b326fcb1-dddd-42e6-8544-4044f5d65272.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093410678-6278bc68-78bf-4a2d-a801-01b60da921c0.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093415704-ed2d3122-5355-44e4-a927-cb4ca4c55d1f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093419841-45f85b7b-a08a-4b33-8790-6cf914c8258d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093419364-998f2948-29ed-49d3-9a34-4dd781e3b141.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093469499-0cdc8f14-80a8-4759-babd-bee74249ed9f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093439101-0175bc3b-4774-4357-a742-8539a48466f0.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093520124-14d39a00-d15c-42f4-bab7-27a0feb2f16b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093512188-cd58e3de-28ef-4245-84d9-6adbb4d88194.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711954141058-d6249382-6ba5-4daa-be68-ab7ba55141ce.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711954146048-627a9a8e-991a-46b1-8951-12e3c92fb8ea.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711954151341-a59a2da6-d0cc-46ad-bd83-ca16cea1ea28.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711954156569-3d500fdd-6315-4cf5-80cf-a255965808a4.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093632109-fbc33206-8e2d-417c-87d2-736f02a9aedb.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093594893-13ce46b6-92d4-4498-aedb-e4886ff74a05.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093768597-a7ebbc84-4ca4-4d1a-a049-5968559129a7.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093772819-9791fca7-139e-49af-b3d2-e309de06f0df.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093776256-f46cfa29-16ca-4191-ba1f-8b94515a4dbc.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093780785-3d407606-c14c-410a-8243-a3b1663f7d63.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093784816-a85c2dc5-7e7d-449f-850f-730e8f8f0306.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093788289-789d477e-d6ed-4982-bd26-b86f913a58f4.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093791855-d7fd537f-eff9-4d3d-97ab-c81ab2572e2d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093795608-7490823b-f623-40a4-8c20-1b4588c1d476.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093799312-9579985f-d0c4-46ee-a809-59e00c60b811.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093804694-d052fe3c-1e4c-4592-bca3-89aeaaa9dd11.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093903063-0d2f604d-fd43-424f-88fa-1d1343670af3.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093887407-8ad37abb-fca6-4233-9d59-8b01fb3742d9.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094049191-4e212ab8-0910-4a19-a7be-2d04e1de1e2a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094053057-4fb1e2f5-706f-432e-8a22-691ca7017b00.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094058174-00ae3bc6-0d09-47b7-a29f-1995fafdb0db.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094061451-a6371e24-5c24-4ef2-864e-9c87e62ca4ee.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094064572-3f36ff75-b8ea-4e35-8e26-56a46a54e6e6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094119575-10dc8996-aa28-41f4-b26e-3c9f79e9abec.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094086642-8d473cab-e9e8-4282-a1f6-aaa59962a00d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094285009-ffe09d51-3c5b-4709-ab0d-60f60016514d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094288990-39cedbb3-ce31-41a1-b2d2-afd4ebfb6efa.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094295063-18c48061-99b2-4ae5-b10b-bc43c6fa9568.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094297859-be39abf7-9bf5-45ea-8905-72869f1320a7.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094302741-37cfa2b1-ed25-445c-8e03-ae75e646954b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094306336-ed206c69-bbaa-4942-9242-8558ef7fb0d3.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094309826-e49f857a-b115-4de0-afdc-dbf81fa3700b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094313393-e0085e2c-57ea-4197-a11c-76ca76a74bbd.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094385188-08d55248-7162-4794-8e63-2d21400a8246.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094329184-5fa999d6-e5d5-4339-b97f-fd460d9ce259.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094439182-52ff6033-e298-4042-a2cd-e80fc5929be9.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094441873-ab3dc817-626a-4605-a38d-bb267539af1a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094512616-274050df-7948-462f-9ef6-a8ce65526a01.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094483441-21a83128-9d1e-4e37-b735-0c09138a77f5.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094701656-c68af08c-9068-48e0-85bd-1ff81f17bcc8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094705028-ce1987d9-2484-4445-b6c0-45de8328b23e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094711291-008842af-5cee-42a6-8175-68966102005d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094714515-481975f1-baed-47c4-bebb-5baf6e13da13.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094719002-a264270f-f004-4d4e-9aaf-fe243b08ff92.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094722850-6d62683d-dbf0-4a57-b0ca-ff9f4576c861.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094754760-8268cecb-91a3-479d-9e5b-8ab7c1db3ddf.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094794474-0be03325-2e5b-4643-9fd4-f75c72aa0cb5.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094775416-224b7b5a-dc49-491a-97ec-6045a8ac971c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094844861-2b84ff9d-9d0b-40d0-ac61-87c950860ceb.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094850423-2b7dbb26-4183-45a4-bb39-d0fb9ad271f6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094853968-69453e59-d46d-4095-adee-d0a1cdcb5123.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094857280-6b0dab89-0658-4200-a17f-b46f21655c96.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094863042-dfcd2db6-b6ab-47a5-a123-79bf126f035c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094912704-ce8055f3-8271-4b29-88c0-f1394c854c66.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094894231-ba71b563-f43c-4ec6-a06c-bc8182a8bafb.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094971820-6990516d-9f59-49fa-9478-1e88d2a9fbbe.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094975871-18971a27-5a83-4b47-bbac-2140c8dfc0e2.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094983138-ca93a4f7-a2a3-4140-9d92-8a48fe5fa503.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094986169-637b581c-b66a-445d-ab0d-43dc1825e1b4.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094993541-ac26d63d-5dcb-4027-ab88-e5f4d450ac8f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095071863-03c3d00a-ff17-4c78-900c-d18f4d37151c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095025487-7acabdec-0b55-4c1a-9918-887b05f9d937.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095141709-c4167344-033c-495c-98ae-e761f12e1be1.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095145275-e805107a-641f-4731-8cd3-1db48dfcdef5.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095148731-d8ba50b3-40fc-4116-bd8f-fe845b14ae95.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095152502-e043ea6c-9244-4507-97ed-fc6da7bfedfa.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095156223-b926157c-eda5-4128-b421-910ab983b445.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095160860-96183607-076c-481b-b7eb-c93c63581232.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095211129-065bebb0-e043-4862-826d-c28bfe9f4631.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095197060-117cd5fa-045b-421f-b457-29a0f60cae3e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095293330-95f83147-e5eb-4b18-a7aa-4dffaef3d5b9.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095296692-20096fb1-0864-4bdf-bbaf-831e43d597ca.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095302867-2e9c738d-4ecc-4612-a56e-dcc3400cf81b.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095307087-ae790053-5e62-425c-bd08-e9b5f30cb4b0.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095312259-3c01b88b-11e9-4d8c-b06e-e3ff901f0efa.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095315727-d93f3b08-7507-4f2d-ad7d-d769485d576f.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095318907-a3dda62b-3d50-4acc-9a52-12200fd42a75.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095381421-8d04e2c8-7dc6-418c-a2a1-6157df7a9f3c.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095342183-a1918d59-84c1-4a25-8697-a6b0c136f3bb.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095423654-ab69048c-f354-4d29-b974-0a5f0f203517.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095427392-ee7cee4a-8b1d-40ff-bf1f-b5f835a25ab2.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097091165-713c6958-1912-489f-875c-25466f7f14f8.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097063547-1b7c756a-89a6-4487-945e-20732069de42.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097136038-6b37eb8d-a93c-4a8f-9bc1-d80230771e88.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097139392-7d85fca9-6c01-4375-aebe-084dd4171405.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097143408-fd6e6ebb-3a6b-4214-98a2-2ed8b4638efd.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095462925-417e9291-bd2a-42f9-95c5-a5e59427fd01.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095512079-62c61223-118e-45be-b2e0-25b01b0e4908.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095552042-bb848d87-11d6-43a3-a3f7-74a8cf41ef75.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095530493-96746779-3005-4ca1-875e-49dd5edda2d1.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095582653-11bda77a-990e-4805-846e-0436d920f136.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095671097-f6118f35-3971-4a6a-ac66-bf7daa64df53.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095653066-d11f7c8e-8522-445d-8502-0f469995efe8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095688758-f6da3eba-6c4a-4bc4-85f9-0f2877e45df3.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095716183-b9e04969-9e90-42b0-9465-d52de1c2661d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095703224-a91a3f33-70ed-4312-bb91-532636c26eb6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095840112-3c07e2f9-589e-4c08-b228-b9b3a7ce0b13.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095802546-0bd8bfeb-c29e-475c-b2e4-f70076d035ee.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095901435-9f6949ce-7cc4-41f8-b15d-081897bb2c4e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095861147-231563e7-c3ca-4ac2-b6d8-778c3ea4984c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096131460-0a02e83d-7be4-4808-b247-a56857033ae1.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096109186-ccb48228-2d46-494f-a622-911e0ffbd54a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096176760-56ae7bf1-4d92-4d8d-968b-512be95719fc.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096164469-c52d34eb-d247-4c95-8ff9-6567aa54badc.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096199943-017db7c7-02c9-419e-b2de-df01cc485c18.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096250696-53830e23-0179-4c86-afba-5b55a671fb92.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096239126-150977e6-bc55-4f4a-b1d4-64d8c8e4444b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096268512-9e6ad9f2-8521-4dda-b5c0-20cf443da178.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096305558-625b1204-9920-478b-abd0-36013bdb274a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096283559-5f67bfb4-ab6d-4948-8395-1fab225a0059.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096440604-6ef72aca-9bab-4dbe-928d-8877823796e7.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096413482-edc38b4b-0056-4793-8030-1a652ba1edba.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096562789-7d1adc83-cd19-4872-87ac-55c9807f48a4.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096582622-538e0833-9ad5-460e-b667-f00f23b426ba.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096604479-b4b32a22-5968-469a-9d6f-0e14e7cf49e5.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096595366-bc9b13f3-215a-48f9-9cd2-b13e09976c66.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096659034-bf7f22b0-76e0-4ccf-b0c6-7860937b153a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096641329-29c0267c-42fa-47e8-a508-5d8f62c77670.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096699007-92feabe8-e2ca-4ce1-bccf-b3691338f15c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096684645-845802eb-a322-4fca-8857-e330724ddb6e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096749935-667e7e18-44b7-4a8e-977e-0e07a2494f14.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096757833-ad4a6931-5682-4c57-b528-53d669f08e1e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096831692-10c4363f-6d4e-4a49-b939-5b3f4407767c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096842792-e831d514-a9e7-420f-920f-cd273b693650.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711096851581-fd8c045b-4973-473d-a209-414b6a10f815.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097174580-ac2324e2-5cc7-449f-a560-2648d6af1e44.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095249853-d3c20042-8d50-495a-896b-2cc1fe9bbc21.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095108194-0f17b0c4-ab4e-41b4-a3f5-f0b5cb1634b8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094944780-b8b1e5e5-6243-4187-9c9b-01082cd85baa.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094814692-0bfc6743-3370-4e2b-9308-2145d8530657.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094666711-95611fa2-fc69-4bfd-b7a5-9562fddfb2ca.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094405679-83e82ebf-e6ae-4971-bb9c-3b4304be82f9.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093558646-5d068ba0-9e6a-45c5-a072-fd99eadef3d3.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093554401-a74a03ab-adf2-4794-b85f-7cf11deea75f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097311949-af205bfd-0138-4eac-9bed-c5af220cce3e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090756674-cd49ca6c-0edd-44eb-9f5a-fe0dc2d3d79e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091015194-478d87f1-a04b-4473-a575-090a9501e488.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091021237-5b21174f-a827-4bd9-a7c6-7b8cf70ec0e6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097105531-cff2a707-8e7b-41bf-86b0-770ac629b9e1.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095401393-501c3ec2-ac75-41db-8c38-380be96dcf3b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091476785-dda7346a-3089-464b-9b8b-f5775c3fb23e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092974402-2e40f02d-ba4c-41d7-b849-a694d87a7ab8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093148786-c08b42a5-0340-4de0-8feb-4ba382b0640f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093153513-d34b145f-af18-431e-867c-42bfaf2c3c2d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093330390-1e7a031f-79a0-4355-a70f-4e006283ffe5.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093720966-ffbfdbe0-7c56-4443-9f66-82ce5f9981ac.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093987937-8bec2c49-3a70-41f4-a0ab-b9e3114cf1b0.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094137866-f53dee58-6fff-40d7-8cfa-6ffae3ecfad9.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094143680-5070db54-73d6-42a5-8852-5e8d4955a836.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097688568-6ed29add-614c-45ef-a01f-aef6606a5ba0.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095256055-54e18c5e-cb57-469b-bdfb-933bcbf2de36.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095112902-de7fe3b5-f4e4-4038-9cba-04139f55636f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094951202-df8b1901-939f-4772-b282-6e9d7588267c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094818460-c31a031e-3fa8-41bc-b6d6-cb9a67f4a923.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094648249-226b0a2b-6ae0-402d-a575-03c1910c148d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094411279-57d8e5f0-1ffc-477c-8114-62c91a5604c4.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093562405-a6e02e95-6bfb-4d1d-88fd-d4a86b31505a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097733374-7e6f3c43-7ca4-4ff1-bcdf-19a61faaad6f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090767284-7221e8a6-2789-45f8-9495-4ebb18bdbef7.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091026315-08d99a1a-d5f2-4810-badf-956253e058e6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097108809-60aa6d2a-1d9e-4458-b6b2-5450b0779e0f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095406127-10ddca8d-9e87-4f38-af59-c0774b128acd.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092979159-4bd7e456-8764-42af-bef2-a2b1e37a575e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093157965-fafff07c-7148-43b8-a47e-96291960f4ca.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093361622-bd54e10e-da7d-445b-863d-67270e607a4d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093725270-2e65d96e-037b-467e-94e6-6e4de0340112.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093995263-6bb9a506-8f92-4264-8729-c35db547cb20.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094147377-7e360f23-f50d-47f2-94bc-77cc7debe573.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093480333-6c061123-d1c0-47c8-9ea5-96230cbb59bb.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097447832-2ac32847-7711-4be7-8db3-a36460014921.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095285192-4eb33dd5-4510-4b5f-9586-8fda293e0dc6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095268445-bc2dede6-0174-4d8c-ae47-d800b58430e7.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095274990-2b93df16-49a0-46b6-89bc-1e18466db646.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095125448-82a81243-d04c-4a2b-871d-a1987c862b64.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095129117-67768733-7846-4695-a051-e516b3566e64.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095134541-1fac2301-44d6-491f-afc3-f48b8c5af977.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094830668-5df956c3-d932-48d0-8b87-cea5466c28ab.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094684530-60180e19-9f01-4553-b724-6e36b510835b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094691923-48cf37d5-85c2-453b-a6e4-ed272bca88c4.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094428752-910ab5b2-79ca-4d8a-8bde-568dd01a3d3a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093575778-6401d904-7656-4c9e-99e0-780795309918.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093494678-cb55f2e6-d19a-4ff9-b0e9-bd99ac64e48a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097494275-e4e3a661-2db5-466e-9811-385032f10c4c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090778867-7140f463-ea6a-4dd0-a8d9-072ffd22ebed.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090789393-0163cd92-88c2-4444-adf6-934efe1c0ca1.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090818481-512404da-00ae-4640-9a63-ce06d333ee34.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090825060-d7e962ad-f8ba-4bf8-b8f2-1fa575b49be8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091038458-0880d6f1-2a24-46f3-843a-f77604e7bbd6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091043865-3d2c9099-3e0f-4fb6-9349-8de57469f9d6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091050226-d9b061fa-4619-48f4-af14-4af67b6840b0.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097117239-1d5d2546-99f4-4591-8ced-0a1bab96b0f3.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097124853-9161b4e2-3a9f-4a7c-9627-37b68947e70f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091494763-4fd3c39c-4ac7-45ae-9955-9968e9834711.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092573138-b7feb6d4-8ee0-4d98-85dd-05784d330c4a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092579394-4f75733b-6aca-48f9-8841-4dd4a79c4372.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092989724-6b94c7ec-db1e-4ebf-986a-e9bb2ca66970.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093000468-a717b715-ecfd-4ac0-9726-845bba2f64aa.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093003977-0036b504-8d88-4354-98b3-0efe378bca0a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093011783-e25dbb4b-0dde-4ee6-96a7-111896e9d60f.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093168780-fa592266-40c6-454f-bffa-6757b699acc8.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093172321-b818ef97-1cc5-43b6-8460-e89e79ed3bdb.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093175884-674d7b20-a844-4faa-a566-42d384b3b9a2.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093181286-2b669550-66d8-4ca0-92db-4215a696aa40.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093375166-f2aa6c67-349b-4175-a2f5-da214db1d4a5.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093378159-5209dbb7-99a7-4b25-a1b6-524175d78f32.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093383130-2d8900ae-e4d3-44fd-a716-721c4e98bd53.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093737197-6e6b17fa-eda2-46ee-9f00-9961060155ce.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093744333-0b81b36e-3521-4150-9873-905e48673d2b.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093751739-10080bdf-c04e-4de8-8457-c470445a4b61.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093756416-d3d1de12-ab2c-4a29-b6f2-ba3153962ae6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094006564-a36f221f-de50-4d6f-9939-cc035f5c1786.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094014730-b430d32e-33f8-4466-bf81-aa2444f79741.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094018201-3a922630-ab17-44bd-8b64-94e1c1e3bb79.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094157167-9f6a31c2-9521-427d-8816-b900be22905d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094161675-16d7b50c-265c-45e2-b0e9-0da53229bd8a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094166102-c3db9f42-0035-4552-bac7-6415ebe39d51.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094170058-e02b7cd1-8565-44d1-ad2c-94d1a18ae29c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097538823-844d292d-6dc5-43a7-9131-fc251a93c5f9.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097566942-86b87164-955e-4471-9dfe-755b2aafb4b4.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095281383-240b61b7-fd20-48a6-aa9b-bf50d11ba824.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097772018-04af34da-380f-4e9a-9baf-b48557eb4411.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097805669-94b5477d-c028-45c9-bc88-43e0c6af7a19.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711090783921-12a557c5-ccce-42e1-a666-97107fdabfde.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711091490042-f99b7ee1-b298-4a7a-adf5-2df910a45187.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092993769-b9c76437-2a67-4458-b11b-9a21aaec8731.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093732978-39614a67-82ea-433a-a4df-d1807329e414.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094010022-223c5fb0-c6d0-414a-b562-75a84840ca72.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097397810-dfc07201-62a5-4dd9-86d8-1a736476f754.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094964926-5baecc26-9087-4bbe-b7cd-771217b6343a.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094837153-439f09e2-e62b-424a-ad65-50f115a510ae.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094432547-81b8efd3-0123-417a-9fe5-5868c4c98666.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093581322-6715c357-4abd-43b4-b48e-1b3a5c040361.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097430620-f513f77a-1036-4641-8c57-ebe8a60d5b6e.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711097128192-bb6812f6-066c-4ef6-a3c7-7056db5eb27c.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711095417062-1ce6445e-bb7f-4ee0-bbb0-764490d0ddf0.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711092583367-ba4ef114-3e1f-4e58-8379-b611598439af.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093017859-bdf377c8-642a-4ca9-b00c-be888c86c654.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093184424-a2d3fdbc-72f4-4769-b459-a3cca3ac882e.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093388885-8f839f4e-9e60-4812-b193-43829783992d.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711093761674-eef85844-faf9-4d1f-97d6-dfd781cf2cd6.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094025484-571c2b56-b5d0-4ef2-9fba-f5f459db0099.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1711094175960-51df915f-dc26-4d05-81d4-4378c1a2fca9.png",
#   "https://cdn.nlark.com/yuque/0/2024/png/23054664/1710326574382-47664661-ecd9-4da8-9097-c5d9af8b724c.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1710326631074-5fc3705d-9cab-4718-b7c2-24014dbd622f.png",
  "https://cdn.nlark.com/yuque/0/2024/png/23054664/1710326733491-8632b005-cc9c-4f50-a6b5-e80897e811f9.png"
]

def get_yjwj_eas_response_map():
    global yjwj_eas_map
    return yjwj_eas_map

def get_yjwj_ocr_waiguan_list():
    global yjwj_ocr_waiguan_list
    return yjwj_ocr_waiguan_list

def get_yjwj_ocr_faxing_list():
    global yjwj_ocr_faxing_list
    return yjwj_ocr_faxing_list

def requestImages():
    monitor_task_status(ENV, "图片下载", "GET")
    for i in range(len(allImages)):
        url = allImages[i]
        response = requests.get(url)
        if response.status_code == 200:
        # 构建图片的本地路径
            file_path = os.path.join(ST.LOG_DIR, f"zzzz_{i}_{str(int(time.time()*1000000))}.jpg")
            # 保存图片到本地
            with open(file_path, 'wb') as file:
                file.write(response.content)
            monitor_print(f"Downloaded {url} to {file_path}")
        else:
            monitor_print(f"Failed to download {url}, status code: {response.status_code}")

def getZZZZImagesPath():
    monitor_task_status(ENV, "图片存储", "GET")
    scriptPath = ENV.logPath
    files = os.listdir(scriptPath)
    allPaths = []

    for file in files:
        if not os.path.isdir(file):
            if file.startswith('zzzz_'):
                allPaths.append(file)
    return allPaths


def ocrTargetImages(image, topleft=(0,0), bottomright=(1200,1200), ocrKey=''):
    monitor_task_status(ENV, "图片OCR", "GET")

    newPath = cropItemPart(image, topleft, bottomright)
    resultList = ocr_image(newPath, en_ocr=False)
    print(f'resultList aaaaaaother:{resultList}')
    needBreak = False
    if resultList is not None:
        for item in resultList:
            if len(item) > 1:
                ocrTitle = item[0]
                ###check 一致性
                if ocrKey in ocrTitle:
                    needBreak = True
                    break
            if needBreak:
                break
    return needBreak

def fenlei_images(images):
    monitor_task_status(ENV, "图片分类", "GET")
    fenleiList = ['名片', '外观', '版本']
    newMaps = {}
    for image in images:
        needBreak = False
        key0 = '发型'
        if ocrTargetImages(image, topleft=(1591,120), bottomright=(2398, 630), ocrKey='发型'):
            if key0 not in newMaps:
                newMaps[key0] = []
            newMaps[key0].append(image)
        else:
            newPath = cropItemPart(image, (0,0), (500,120))
            resultList = ocr_image(newPath, en_ocr=False)
            print(f'resultList fenlei_images:{resultList}')
            if resultList is not None:
                for item in resultList:
                    if len(item) > 1:
                        ocrTitle = item[0]
                        ###check 一致性
                        for fenleiTitle in fenleiList:
                            if fenleiTitle in ocrTitle:
                                if ocrTitle not in newMaps:
                                    newMaps[ocrTitle] = []
                                newMaps[ocrTitle].append(image)
                                needBreak = True
                                break
                    if needBreak:
                        break

        if not needBreak:
            key1 = '版本'
            key2 = '神识等级'
            key3 = '主页'
            key4 = '通行证等级'
            key5 = '充值'
            if ocrTargetImages(image, topleft=(0,0), bottomright=(2000,200), ocrKey='版本升级'):
                if key1 not in newMaps:
                    newMaps[key1] = []
                newMaps[key1].append(image)
            elif ocrTargetImages(image, topleft=(0,0), bottomright=(2000,200), ocrKey='充值'):
                if key1 not in newMaps:
                    newMaps[key5] = []
                newMaps[key5].append(image)
            elif ocrTargetImages(image, topleft=(0,0), bottomright=(500,300), ocrKey='英雄币'):
                if key2 not in newMaps:
                    newMaps[key2] = []
                newMaps[key2].append(image)
            elif ocrTargetImages(image, topleft=(0,0), bottomright=(600,260), ocrKey='每日任务'):
                if key3 not in newMaps:
                    newMaps[key3] = []
                newMaps[key3].append(image)
            elif ocrTargetImages(image, topleft=(0,0), bottomright=(600,300), ocrKey='赛季奖励'):
                if key4 not in newMaps:
                    newMaps[key4] = []
                newMaps[key4].append(image)
            else:
                if '其他' not in newMaps:
                    newMaps['其他'] = []
                newMaps['其他'].append(image)

    monitor_print(f"fenlei_result ------------:{newMaps}")

    return newMaps

# 裁剪图片 - 特地尺寸
def cropItemPart(name, fromPoint, toPoint, need_snapshot=False):
    file_path = os.path.join(ST.LOG_DIR, name)
    with Image.open(file_path) as img:
        # 获取图像的尺寸
        width, height = img.size

    fromPoint = (int(fromPoint[0] * width/2368), int(fromPoint[1] * height/1326))
    toPoint = (int(toPoint[0] * width/2368), int(toPoint[1] * height/1326))
    target_path = 'crop_left_top_type_' + str(int(time.time()*1000000)) + '.jpg'
    crop_pos_image_from_snapshot(name,target_path, fromPoint, toPoint, need_snapshot)
    to_path = os.path.join(ST.LOG_DIR, target_path)

    return to_path

def getRequestDataListWithURL(url, propertyIdList, expCount=11, needBox=False):
    resData = {}
    resData['imageProperties'] = [
    ]
    global  shibieMap
    if 'all' not in shibieMap:
        shibieMap['all'] = []
    for item in propertyIdList:
        if item == '外观' or item == '发型':
            resData['imageProperties'].append(
                {
                    "propertyId": item,
                    "optionList": shibieMap['all']
                    # "expCount": expCount
                }
            )
        else:
            resData['imageProperties'].append(
                {
                    "propertyId": item
                    # "expCount": expCount
                }
            )

    resId = str(int(time.time()*1000000))
    resData['requestId'] = resId
    resData['imageUrl'] = url
    resData['recoType'] = "永劫无间PC"
    if needBox:
        resData['needBox'] = True
    return resData

def getImageURLWithPNG(filename):
    match = re.search(r"zzzz_([0-9]+)_([0-9]+)\.jpg", filename)

    urlString = ''
    first_number = -1
    if match:
        first_number = match.group(1)
        if first_number is not None and first_number.isdigit() and int(first_number) < len(allImages):
            urlString = allImages[int(first_number)]
        monitor_print(f"第一个数字是: {first_number}")
    else:
        monitor_print("未找到匹配的数字。")
    
    return urlString

def getWaiguanEAS(aMap,requestKey='外观',idList=['外观']):
    waiguanList = []
    easMap = {}
    if aMap is not None and requestKey in aMap: 
        waiguanList = aMap[requestKey]

    if waiguanList is not None:
        for waiguan in waiguanList:
            
            url = getImageURLWithPNG(waiguan)
            if url is not None and url != '':
                res = easRequest(get_env_risk_path(), getRequestDataListWithURL(url, idList, needBox=False), preUseLocal=True)
                if res is not None and 'message' in res and ('imagePropertyValues' in res['message']):
                    values = res['message']['imagePropertyValues']
                    for value in values:
                        if value['propertyId'] in idList and 'value' in value:
                            valList = value['value']
                            if valList is not None and len(valList)>0 and 'text' in valList[0]:
                                easMap[value['propertyId']] = valList[0]['text']
    
    monitor_print(f"easMap_end:{easMap}")
    return easMap

def getAllPifuEAS(aMap,requestKey='外观',idList=['外观']):
    waiguanList = []
    resultList = []
    lockedList = []
    if aMap is not None and requestKey in aMap: 
        waiguanList = aMap[requestKey]

    if waiguanList is not None:
        for waiguan in waiguanList:
            
            url = getImageURLWithPNG(waiguan)
            if url is not None and url != '':
                res = easRequest(get_env_risk_path(), getRequestDataListWithURL(url, idList, needBox=False), preUseLocal=True)
                if res is not None and 'message' in res and ('imagePropertyValues' in res['message']):
                    values = res['message']['imagePropertyValues']
                    for value in values:
                        if value['propertyId'] in idList and 'value' in value:
                            valList = value['value']
                            if valList is not None and len(valList)>0:
                                for val in valList:
                                    if 'text' in val and 'lock' in val:
                                        if val['text'] in lockedList:
                                            monitor_print(f"protect_waiguan_chongshifu :{val['text']}")
                                        if val['lock'] != True and (val['text'] not in lockedList):
                                            resultList.append(val['text'])
                                        else:
                                            if val['text'] in resultList:
                                                monitor_print(f"remove_faxing_chongshifu :{val['text']}")
                                                resultList.remove(val['text'])
                                            lockedList.append(val['text'])
                                #  and 'text' in valList[0] and 'lock' in valList[0]:
                                # if valList[0]['lock'] == True:
                                #     resultList.append(valList[0]['text'])
    
    monitor_print(f"resultList_end:{resultList}")
    monitor_print(f"unlockedList_end:{lockedList}")
    return resultList

def getAllFaxingEAS(aMap,requestKey='发型',idList=['发型', '锁']):
    waiguanList = []
    resultList = []
    lockedList = []
    if aMap is not None and requestKey in aMap: 
        waiguanList = aMap[requestKey]

    if waiguanList is not None:
        for waiguan in waiguanList:
            
            url = getImageURLWithPNG(waiguan)
            if url is not None and url != '':
                res = easRequest(get_env_risk_path(), getRequestDataListWithURL(url, idList, needBox=True), preUseLocal=True)
                if res is not None and 'message' in res and ('imagePropertyValues' in res['message']):
                    values = res['message']['imagePropertyValues']
                    for value in values:
                        if value['propertyId'] in idList and 'value' in value:
                            valList = value['value']
                            if valList is not None and len(valList)>0:
                                for val in valList:
                                    if 'text' in val:
                                        subValString = re.sub(r"【.*?】", "", val['text'])
                                        if subValString in lockedList:
                                            monitor_print(f"protect_faxing_chongshifu :{subValString}")
                                        if val['text'] != '锁' and (subValString not in lockedList):
                                            resultList.append(subValString)
                                        else:
                                            if subValString in resultList:
                                                monitor_print(f"remove_faxing_chongshifu :{subValString}")
                                                resultList.remove(subValString)
                                            lockedList.append(subValString)
                                #  and 'text' in valList[0] and 'lock' in valList[0]:
                                # if valList[0]['lock'] == True:
                                #     resultList.append(valList[0]['text'])
    
    monitor_print(f"resultList_faxing_end:{resultList}")
    monitor_print(f"lockedList_faxing_end:{lockedList}")
    return resultList


def renameADCResultImages(aMaps):
    monitor_task_status(ENV, "图片重命名 - 回传到任务", "GET")
    for key in aMaps:
        if key != '其他':
            imageList = aMaps[key]
            for image in imageList:
                original_filename = os.path.join(ST.LOG_DIR, image)
                new_filename = os.path.join(ST.LOG_DIR, f"adc_result_{image}")
                if os.path.isfile(original_filename):
                    # 重命名文件
                    os.rename(original_filename, new_filename)
                    if key == '主页':
                        #主页保留一张即可
                        break

def getPinshuEas(aMaps):
    newMaps = {}
    easRes = getWaiguanEAS(aMaps,requestKey='名片',idList=['红品数', '金品数'])
    if '红品数' in easRes:
        newMaps['红皮数'] = easRes['红品数']
    else:
        ##重试一次
        easRes = getWaiguanEAS(aMaps,requestKey='名片',idList=['红品数', '金品数'])
        if '红品数' in easRes:
            newMaps['红皮数'] = easRes['红品数']
        # else:
        #     lx_break_runloop(desc="红皮数信息失败")


    if '金品数' in easRes:
        newMaps['金皮数'] = easRes['金品数']
    else:
        ##重试一次
        easRes = getWaiguanEAS(aMaps,requestKey='名片',idList=['红品数', '金品数'])
        if '金品数' in easRes:
            newMaps['金皮数'] = easRes['金品数']
        # else:
        #     lx_break_runloop(desc="金皮数信息失败")
    
    return newMaps

def rename_response_eas_map(easMap):
    if '神识等级' in easMap:
        easMap['神识(征神)等级'] = easMap['神识等级']
        del easMap['神识等级']
    if '幻丝' in easMap:
        easMap['幻丝数'] = easMap['幻丝']
        del easMap['幻丝']

    return easMap


def startTask():
    global yjwj_eas_map
    yjwj_eas_map = {}
    monitor_task_status(ENV, "start", "GET")
    global allImages
    ##### ENV.image_list_json = "{\"all\":[\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/5ff0034f-3fbc-4567-8a04-fb627c953e95.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/8d218bd6-e638-4afc-9c88-dd0aeab0b315.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/3369db03-355b-4e3e-b024-3264c4c052d2.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/3808779f-25e6-4cc3-a721-93fdb111f4b9.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/39e6f17c-d4b4-41c3-a73f-e09e315db64e.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/7eb8850b-1d34-4811-b314-5320f07e9a3f.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/7c499318-195f-481f-9ea1-aa001e0b0f5c.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/6fc7ff3a-3658-4bf6-a2a7-e73b687740bd.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/594c15d4-9530-48cb-aee7-36d8f927368a.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/03b5cf3b-3d2b-4215-8e30-eb1b4e2ce99f.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/cb85e43e-e651-4c6e-b30c-93bc93672566.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/3ca4d98b-70ea-4fa0-86fc-d64d78185fc3.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/0f167299-65db-4ef0-973f-a3e1cc129b77.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/6ace6793-71d0-42a8-a47a-be2fecbd25a8.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/15dc11a1-14ce-4cee-8029-6dee2b432fd6.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/12eff97b-d844-4435-9180-0c58b2668dd2.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/13cb9c6a-f57c-4c17-9da8-d95e98606a67.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/aa464138-e6bf-4890-908f-e9da778e8c25.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/bb26cc39-f52d-4074-8f22-77c374125a72.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/2245f756-61da-437e-89ec-ce48fa630f52.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/a48e032d-d90b-43ff-a34a-968507e572f2.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/75e0d29a-f829-45d8-a4ea-ec893d3f0878.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/b8f68824-7d10-43d0-8a84-3fc0f8f23bc7.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/7d0e5bc0-5486-4933-93c3-b5fbaf0cb4d1.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/f86c8b1a-4cc0-4fbc-8a8d-5d8df63c7d55.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/b57291c9-4d45-4259-b13e-dc0b5ef085b7.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/3ed96606-f74a-447f-8f4f-874a2d90a012.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/23bfaf4d-50b9-4b6d-b320-e04144a98c5b.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/8b7932e3-1286-418c-8044-62adc735495e.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/0f5a206f-4101-4d9d-8467-5c0e550c8bc1.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/e6128a54-2046-4b75-80eb-f62319fd4c7c.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/598f2cfb-3bc9-4b52-9fff-e44bb6fdae60.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/4bcfb775-0121-40e6-9141-58a389a9a37a.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/b1cf16e0-a10c-44c9-8ceb-b6144bd7c5c3.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/312cf4d9-5e58-47f2-91e7-f04e134892ca.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/73c84fe3-00c1-4ba7-bd59-fdf2182b2c55.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/af0ff1c4-f2e1-4f2b-ab60-229ee8f255a1.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/4473f2f5-36eb-49ab-8d54-d6a078764c18.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/ce95d2f2-5535-47ac-aa9b-9a36cce0bfd7.jpg\",\"https://static-cdn.jiaoyimao.com/jym-oss/resource/gcmall-fs/file/chat/2024/4/10/433959fe-6e28-47a2-a77c-50458cea7497.jpg\"]}"
    serviceMap = json.loads(ENV.image_list_json)
    if 'all' in serviceMap:
        allImages = serviceMap['all']
    else:
        lx_break_app(desc='数据解析失败', ext_info={'key':'10111'})

    requestImages()

    allDownloadImages = getZZZZImagesPath()
    monitor_print(f"------------:{allDownloadImages}")

    resEasMap = {}
    fenleiMap = fenlei_images(allDownloadImages)

    result = getWaiguanEAS(fenleiMap,requestKey='版本',idList=['版本'])
    if '版本' not in result and '充值' in fenleiMap:
        checkMap = {}
        checkMap['版本'] = '终极版'
        resEasMap.update(checkMap)
    resEasMap.update(result)

    resEasMap.update(getPinshuEas(fenleiMap))
    resEasMap.update(getWaiguanEAS(fenleiMap,requestKey='神识等级',idList=['神识等级']))
    resEasMap.update(getWaiguanEAS(fenleiMap,requestKey='主页',idList=['幻丝', '金砖']))
    resEasMap.update(getWaiguanEAS(fenleiMap,requestKey='名片',idList=['三排段位', '角色等级']))
    resEasMap.update(getWaiguanEAS(fenleiMap,requestKey='通行证等级',idList=['通行证等级']))
    

    renamedResEasMap = rename_response_eas_map(resEasMap)
    monitor_print(f"resEasMap_yongjiewujian ------------:{renamedResEasMap}")
    ####结束后重命名图片
    renameADCResultImages(fenleiMap)

    yjwj_eas_map.update(renamedResEasMap)


    ##### =================== #####
    #####      发型+外观       #####
    ##### =================== #####
    global yjwj_ocr_waiguan_list
    global yjwj_ocr_faxing_list
    curWGList = getAllPifuEAS(fenleiMap,requestKey='外观',idList=['外观'])
    curFXList = getAllFaxingEAS(fenleiMap,requestKey='发型',idList=['发型','锁'])

    yjwj_ocr_waiguan_list = curWGList
    yjwj_ocr_faxing_list = curFXList
    
def get_env_risk_path():
    scriptEnv = ENV.scriptEnv
    risk_path = ""
    monitor_print(f"scriptEnv:{scriptEnv}")
    if (scriptEnv == 'local' or scriptEnv == 'daily'):
        risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
    elif (scriptEnv == 'pre'):
        risk_path = '/api/predict/lingxialgo_adc_ocr_pre'
    elif (scriptEnv == 'prod'):
        risk_path = '/api/predict/lingxialgo_vision_adc'
    else:
        risk_path = '/api/predict/lingxialgo_vision_adc'
    return risk_path



# ============================================
def loadPropertyFile(gameProperties):
    monitor_print(f"拉取的多子属性是：{gameProperties}")
    global shibieMap
    shibieMap['all'] = []

    for propertyDic in gameProperties:
        propertyName = propertyDic.get("propertyName")
        if propertyName not in shibieMap:
            shibieMap[propertyName] = []
        kucangPropertyList = propertyDic.get("gameProperties")
        for kucangProperty in kucangPropertyList:
            propertyValue = kucangProperty.get("propertyValue")
            if propertyValue is not None:
                if propertyName == '英雄皮肤' or propertyName == '武器皮肤' or propertyName == '挂饰皮肤':
                    shibieMap[propertyName].append(propertyValue)
                shibieMap['all'].append(propertyValue)
    monitor_print(f"shibieMap属性名称列表为 ：{shibieMap['all']}")

def app_did_get_properties(properties):
    try:
        gameProperties = json.loads(properties)
        loadPropertyFile(gameProperties)
    except json.JSONDecodeError:  # 解析失败，捕获异常
        return
# ============================================
def cleanGame(env):
    # shell("rm -rf /sdcard/37shouyou") 
    # shell("rm -rf /data/data/com.sy.dldlhsdj.gw/databases") 
    # shell("rm -rf /data/data/com.sy.dldlhsdj.gw/shared_prefs") 

    monitor_task_status(env, "清理游戏信息", "")

def closeGame(env):
    # stop_app("com.sy.dldlhsdj.gw")
    monitor_task_status(env, "关闭游戏", "")

def game_will_launch(env):     
    # global gameName
    monitor_task_status(env, "启动游戏", f"启动{gameName}")
    ### start_app("com.dldlhsdj.wzpz1")
    # start_app("com.sy.dldlhsdj.gw")
   


def game_did_launch(env):
    monitor_print('game_did_launch=====index')
    monitor_task_status(env, "永劫无间PC OCR", f"taskType{env.taskType}")

    phaseList = []
    
    phase = Phase("get_images",lambda: startTask())
    phaseList.append(phase)
    return phaseList
    
def game_will_close(env):
    closeGame(env)


def game_will_clean(env):
    cleanGame(env)

def app_will_process_exception_snapshot(snapshot_path):
    monitor_print("app_will_process_exception_snapshot")
    
    
def app_will_process_properties(properties,urls):
    monitor_print("app_will_process_properties")



    



