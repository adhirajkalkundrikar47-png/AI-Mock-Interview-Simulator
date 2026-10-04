package com.interview;

import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebFilter("/*")
public class SecurityHeaders implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletResponse http = (HttpServletResponse) response;
        http.setHeader("X-Content-Type-Options", "nosniff");
        http.setHeader("Referrer-Policy", "same-origin");
        http.setHeader("Content-Security-Policy", "default-src 'self'; script-src 'self'; "
                + "style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'");
        chain.doFilter(request, response);
    }
}
