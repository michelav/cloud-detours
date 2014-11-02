package br.unifor.ppgia.cloud.core;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class DetoursContext {
	
	private static DetoursContext instance;
	
	Properties props = new Properties();
	
	private DetoursContext() {
		InputStream inputStream = getClass().getClassLoader().getResourceAsStream("detours.properties");
		try {
			props.load(inputStream);	
		} catch (IOException ioe) {
			// XXX Handle this correctly
		}
	}
	
	public static DetoursContext getInstance() {
		if(instance == null) {
			instance = new DetoursContext();
		}
		return instance;
	}
	
	public String getProperty(String key) {
		return props.getProperty(key);
	}
}
