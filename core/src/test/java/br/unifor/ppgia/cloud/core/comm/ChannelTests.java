package br.unifor.ppgia.cloud.core.comm;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import java.util.Random;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import br.unifor.ppgia.cloud.core.comm.ChannelProvider.EventType;
import br.unifor.ppgia.cloud.core.comm.defaultimpl.DefaultChannelProvider;

public class ChannelTests {
	
	private static Channel client;
	private static Channel server;
	final static String ENDPOINT = "ipc:///tmp/tests.ipc";

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
		ChannelProvider channelProvider = DefaultChannelProvider.getInstance();
		client = channelProvider.createChannel(ENDPOINT);
		server = channelProvider.createChannel(ENDPOINT);
		client.connect();
		server.bind();
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
		client.close();
		server.close();
		DefaultChannelProvider.getInstance().releaseResources();
	}


	@Test
	public void simpleSendAndRecvTest() {
		ChannelProvider channelProvider = DefaultChannelProvider.getInstance();
		Event ping = channelProvider.getEvent(EventType.PING_EVT);
		client.sendEvent(ping);
		Event srvRecvEvent = server.recvEvent();
		
		assertEquals("Ping request is not working on IPC Channels...", "ping",
				srvRecvEvent.getInfo("control"));
		
		Event pong = channelProvider.getEvent(EventType.PONG_EVT);
		server.sendEvent(pong);
		
		Event cliRcvEvent = client.recvEvent();

		assertEquals("Pong response is not working on IPC Channels...", "pong",
				cliRcvEvent.getInfo("control"));
	}

	@Test
	public void sendAndRecvWithDataTest() {
		ChannelProvider channelProvider = DefaultChannelProvider.getInstance();
		Event loop = channelProvider.getEvent(EventType.LOOPBACK_EVT);
		byte[] payload = new byte[20];
		new Random().nextBytes(payload);

		loop.setPayload(payload);
		client.sendEvent(loop);
		
		Event recvEvent = server.recvEvent();
		assertEquals("LoopBack message is not working on IPC Channels...",
				"loop", recvEvent.getInfo("control"));		
		
		Event back = channelProvider.getEvent(EventType.BLANK_EVT);
		back.addInfo("control", "back");
		back.setPayload(recvEvent.getPayload());
		server.sendEvent(back);
				
		Event cliRcvEvent = client.recvEvent();

		assertEquals("LoopBack message is not working on IPC Channels...",
				"back", cliRcvEvent.getInfo("control"));
		assertArrayEquals("LoopBack message is not working on IPC Channels...",
				payload, cliRcvEvent.getPayload());
	}
}
