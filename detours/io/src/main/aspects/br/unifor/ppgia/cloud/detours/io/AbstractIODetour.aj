package br.unifor.ppgia.cloud.detours.io;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;

import br.unifor.ppgia.cloud.core.comm.Channel;

public abstract aspect AbstractIODetour {
	
	protected Channel currentChannel = null;

	public abstract void allocateResources();
	
	public abstract void releaseResources();
	
	pointcut fileInputStreamCreation(File theFile):
		call(FileInputStream.new(File)) && args(theFile);

	pointcut fileOutputStreamCreation(File theFile):
	call(public FileOutputStream+.new(File)) && args(theFile);

	pointcut fileCreation(File parent, String child): 
	call(File.new(File, String)) && args(parent, child);
	
	abstract pointcut outputStreamAdaptationPoint();
	
	abstract pointcut fileAdaptationPoint();
	
	
	abstract pointcut freeResourcesPoint();

	// around(File theFile): fileInputStreamCreation(File theFile) &&
	// adaptationPoint() {
	// // TODO: Implement behavior.
	// }

	FileOutputStream around(File theFile) throws FileNotFoundException:
		outputStreamAdaptationPoint() &&
		fileOutputStreamCreation(theFile) {
		allocateResources();
		DetouredFileOutputStream dfos = new DetouredFileOutputStream(theFile);
		dfos.configureChannel(currentChannel);
		return dfos;
	}

	File around(File parent, String child): 
	fileCreation(parent, child) && fileAdaptationPoint() {
		allocateResources();
		SimpleDetouredFile file = new SimpleDetouredFile(parent, child);
		file.configureChannel(currentChannel);
		return file;
	}
	
	after(): freeResourcesPoint() {
		releaseResources();
	}
}
