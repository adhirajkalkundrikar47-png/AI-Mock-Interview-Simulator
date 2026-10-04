package com.interview;
import java.nio.file.*;import java.sql.*;import java.util.*;
public interface Store {
 Map<String,Object> load(String id) throws Exception;void save(String id,Map<String,Object> value)throws Exception;
 static Store open()throws Exception{String url=System.getenv("DB_URL");return url==null||url.isBlank()?new FilesStore():new JdbcStore(url);}
 class FilesStore implements Store{
  Path root=Path.of(System.getenv().getOrDefault("DATA_DIR","data"));FilesStore()throws Exception{Files.createDirectories(root);}Path path(String id){if(!id.matches("[a-f0-9]{64}"))throw new IllegalArgumentException();return root.resolve(id+".json");}
  public Map<String,Object>load(String id)throws Exception{Path p=path(id);return Files.exists(p)?Json.obj(Json.read(Files.readString(p))):null;}
  public void save(String id,Map<String,Object>v)throws Exception{Path t=Files.createTempFile(root,"save-",".tmp");try{Files.writeString(t,Json.write(v));try{Files.move(t,path(id),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}catch(AtomicMoveNotSupportedException e){Files.move(t,path(id),StandardCopyOption.REPLACE_EXISTING);}}finally{Files.deleteIfExists(t);}}
 }
 class JdbcStore implements Store{
  String url,user,password;JdbcStore(String url)throws Exception{Class.forName("com.mysql.cj.jdbc.Driver");this.url=url;user=System.getenv().getOrDefault("DB_USER","interview");password=System.getenv("DB_PASSWORD");try(Connection c=connect();Statement s=c.createStatement()){s.executeUpdate("CREATE TABLE IF NOT EXISTS learner_records (id CHAR(64) PRIMARY KEY, payload JSON NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)");}}
  Connection connect()throws SQLException{return DriverManager.getConnection(url,user,password);}
  public Map<String,Object>load(String id)throws Exception{try(Connection c=connect();PreparedStatement p=c.prepareStatement("SELECT payload FROM learner_records WHERE id=?")){p.setString(1,id);try(ResultSet r=p.executeQuery()){return r.next()?Json.obj(Json.read(r.getString(1))):null;}}}
  public void save(String id,Map<String,Object>v)throws Exception{try(Connection c=connect();PreparedStatement p=c.prepareStatement("INSERT INTO learner_records(id,payload) VALUES (?,?) ON DUPLICATE KEY UPDATE payload=?")){String j=Json.write(v);p.setString(1,id);p.setString(2,j);p.setString(3,j);p.executeUpdate();}}
 }
}
