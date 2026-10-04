package com.interview;
import jakarta.servlet.*;import jakarta.servlet.http.*;import jakarta.servlet.annotation.WebServlet;import java.io.*;import java.nio.charset.StandardCharsets;
@WebServlet(urlPatterns="/api/*",loadOnStartup=1)
public class ApiServlet extends HttpServlet {
 private App app;
 public void init()throws ServletException{try{app=new App();}catch(Exception e){throw new ServletException("Unable to initialize storage",e);}}
 protected void service(HttpServletRequest req,HttpServletResponse res)throws IOException{res.setContentType("application/json;charset=UTF-8");res.setHeader("Cache-Control","no-store");res.setHeader("X-Content-Type-Options","nosniff");byte[]raw=req.getInputStream().readNBytes(20001);if(raw.length>20000){res.setStatus(413);res.getWriter().write("{\"error\":\"Request too large\"}");return;}App.Reply r=app.request(req.getMethod(),req.getPathInfo()==null?"/":req.getPathInfo(),new String(raw,StandardCharsets.UTF_8),req.getHeader("Cookie")==null?"":req.getHeader("Cookie"),req.getHeader("Origin"),req.getHeader("Host"),req.isSecure()||"true".equals(System.getenv("COOKIE_SECURE")),req.getRemoteAddr());res.setStatus(r.status());if(r.cookie()!=null)res.setHeader("Set-Cookie",r.cookie());res.getWriter().write(Json.write(r.body()));}
}
