from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# Thông tin kết nối
host = "10.248.242.90"
port = 5000
dbname = "vcc_dw"  # Giả sử "dwh" là tên cơ sở dữ liệu
username = "postgres"
password = "Vcc@123#20200"

# URL encode password
encoded_password = quote_plus(password)

# Tạo URL kết nối
dsn = f"postgresql+psycopg2://{username}:{encoded_password}@{host}:{port}/{dbname}"

# Tạo engine kết nối
engine = create_engine(dsn)

# Tạo session
Session = sessionmaker(bind=engine)
session = Session()

# Thực hiện truy vấn
query = '''
select * from vcc_cntt.online_cntt_ai_project_hop_dong_aio_partner
'''

# Lấy và xử lý kết quả
result = session.execute(query)
for row in result:
    print(row)

# Đóng session
session.close()