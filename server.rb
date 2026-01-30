require 'webrick'
require 'json'
require 'sqlite3'

# 初始化数据库
db = SQLite3::Database.new "leave_system.db"
db.execute <<-SQL
  CREATE TABLE IF NOT EXISTS leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    startDate TEXT NOT NULL,
    endDate TEXT NOT NULL,
    reason TEXT
  );
SQL

server = WEBrick::HTTPServer.new(
  :Port => 8000,
  :BindAddress => '0.0.0.0',
  :DocumentRoot => './templates',
  :AccessLog => [[$stdout, WEBrick::AccessLog::COMBINED_LOG_FORMAT]],
  :Logger => WEBrick::Log.new($stdout, WEBrick::BasicLog::DEBUG)
)

# 处理 API 获取数据
server.mount_proc '/api/leaves' do |req, res|
  db = SQLite3::Database.new "leave_system.db"
  if req.request_method == 'GET'
    rows = db.execute("SELECT * FROM leaves")
    leaves = rows.map do |row|
      { id: row[0], user: row[1], startDate: row[2], endDate: row[3], reason: row[4] }
    end
    res.status = 200
    res['Content-Type'] = 'application/json'
    res.body = leaves.to_json
  elsif req.request_method == 'POST'
    data = JSON.parse(req.body)
    db.execute("INSERT INTO leaves (user, startDate, endDate, reason) VALUES (?, ?, ?, ?)",
               [data['user'], data['startDate'], data['endDate'], data['reason']])
    res.status = 200
    res['Content-Type'] = 'application/json'
    res.body = { status: 'success' }.to_json
  else
    res.status = 405
  end
end

# 让根目录指向 index.html
server.mount_proc '/' do |req, res|
  if req.path == '/'
    res.status = 200
    res['Content-Type'] = 'text/html'
    res.body = File.read('templates/index.html')
  else
    WEBrick::HTTPServlet::FileHandler.get_instance(server, './templates').do_GET(req, res)
  end
end

trap('INT') { server.shutdown }
puts "服务器已启动: http://localhost:8000"
server.start
